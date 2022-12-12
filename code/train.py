import json
import os
import os.path as osp
import random
import time
import math
from datetime import timedelta
from argparse import ArgumentParser

import torch
from torch import cuda
from torch.utils.data import DataLoader
from torch.optim import lr_scheduler
from tqdm import tqdm

from east_dataset import EASTDataset
from dataset import SceneTextDataset
from model import EAST
import cv2
import wandb
import numpy as np
from detect import detect
from PIL import Image
from deteval import calc_deteval_metrics

def parse_args():
    parser = ArgumentParser()

    # Conventional args
    parser.add_argument('--data_dir', type=str,
                        default=os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data'))
    parser.add_argument('--val_data_dir', type=str,
                        default=os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/ICDAR17_Korean'))
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR',
                                                                        '/opt/ml/input/data/outputs'))

    parser.add_argument('--device', default='cuda' if cuda.is_available() else 'cpu')
    parser.add_argument('--num_workers', type=int, default=4) # default = 4

    parser.add_argument('--image_size', type=int, default=1024) # default = 1024
    parser.add_argument('--input_size', type=int, default=512) # default = 512
    parser.add_argument('--batch_size', type=int, default=12) # default = 12
    parser.add_argument('--learning_rate', type=float, default=1e-3) # default = 1e-3
    parser.add_argument('--max_epoch', type=int, default=200)
    parser.add_argument('--val_interval', type=int, default=10)
    parser.add_argument('--seed',type=int,default=2022)
    parser.add_argument('--parent_run_num',type=str,default="010")
    ############## PLEASE WRITE NOTE BEFORE RUN ###############
    parser.add_argument('--note',type=str,default="This will be augmented data steplr testing")
    ###########################################################
    parser.add_argument('--save_top_k',type=int,default=3)
    parser.add_argument("--scheduler_type",type=str,default="MultiStepLR")
    args = parser.parse_args()

    if args.input_size % 32 != 0:
        raise ValueError('`input_size` must be a multiple of 32')

    return args

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed) # if use multi-GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)


def get_scheduler(scheduler_type,optimizer,max_epoch,learning_rate):
    schedulers={
        "MultiStepLR":lr_scheduler.MultiStepLR(optimizer, milestones=[max_epoch // 2], gamma=0.1),
        "StepLR":lr_scheduler.StepLR(optimizer, step_size=max_epoch//4, gamma=0.5),
        "CosineAnnealingWarmRestarts":lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=30,T_mult=1,eta_min=learning_rate//10),
        "MultiStepLR":lr_scheduler.MultiStepLR(optimizer,milestones=list(range(0,max_epoch,max_epoch//3)),gamma=0.5),
        "ExponentialLR":lr_scheduler.ExponentialLR(optimizer,gamma=0.95),
        "CosineAnnealingLR":lr_scheduler.CosineAnnealingLR(optimizer, T_max=50,eta_min=learning_rate//10),
        "CyclicLR":lr_scheduler.CyclicLR(optimizer, base_lr=learning_rate//10,max_lr=learning_rate,step_size_up=20,step_size_down=30,mode="triangular",cycle_momentum=False)
    }
    
    assert scheduler_type in schedulers, "The scheduler is not in the collection"
        
    return schedulers[scheduler_type]

def do_training(data_dir,val_data_dir, model_dir, device, image_size, input_size, num_workers, batch_size,
                learning_rate, max_epoch, val_interval,save_top_k,scheduler_type,**kwargs):
    dataset = SceneTextDataset(data_dir, split='train', image_size=image_size, crop_size=input_size)
    dataset = EASTDataset(dataset)
    num_batches = math.ceil(len(dataset) / batch_size)
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"running on {device}...")
    model = EAST()
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler=get_scheduler(scheduler_type,optimizer,max_epoch,learning_rate)

    model_dir=osp.join(model_dir,this_run_name)
    
    model.train()
    for epoch in range(max_epoch):
        epoch_loss, epoch_start = 0, time.time()
        with tqdm(total=num_batches) as pbar:
            for img, gt_score_map, gt_geo_map, roi_mask in train_loader:
                pbar.set_description('[Epoch {}]'.format(epoch + 1))

                loss, extra_info = model.train_step(img, gt_score_map, gt_geo_map, roi_mask)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                loss_val = loss.item()
                epoch_loss += loss_val

                pbar.update(1)
                val_dict = {
                    'Cls loss': extra_info['cls_loss'], 'Angle loss': extra_info['angle_loss'],
                    'IoU loss': extra_info['iou_loss']
                }
                pbar.set_postfix(val_dict)
                wandb.log({"Train/loss": epoch_loss,'Train/Cls loss': extra_info['cls_loss'], 'Train/Angle loss': extra_info['angle_loss'], 'Train/IoU loss': extra_info['iou_loss'],"Learning_rate":scheduler.optimizer.param_groups[0]['lr']})

        scheduler.step()
        print('Mean loss: {:.4f} | Elapsed time: {}'.format(
            epoch_loss / num_batches, timedelta(seconds=time.time() - epoch_start)))

        if (epoch + 1) % val_interval == 0:
            
            precision,recall, f1=do_validation(model,val_data_dir,batch_size,input_size)
            wandb.log({"Val/precision": precision,"Val/recall": recall,"Val/f1": f1})
            
            if not osp.exists(model_dir):
                os.makedirs(model_dir)
            files = os.listdir(model_dir)
            files.sort(reverse=True)
            if len(files)<save_top_k:
                ckpt_fpath = osp.join(model_dir, str(f1)+f'_{this_run_num}_e{epoch}.pth')
                torch.save(model.state_dict(), ckpt_fpath)
            else:
                worst_file_path=osp.join(model_dir,get_worst(model_dir))
                worst_score=float(get_worst(model_dir).split("_")[0])
                if f1>worst_score:
                    os.remove(worst_file_path)
                    ckpt_fpath = osp.join(model_dir, str(f1)+f'_{this_run_num}_e{epoch}.pth')
                    torch.save(model.state_dict(), ckpt_fpath)

            
    best=get_best(model_dir)
    artifact=wandb.Artifact('model_pth',type='model')
    artifact.add_file(osp.join(model_dir,best))
    wandb.log_artifact(artifact)

def get_best(dir):
    files = os.listdir(dir)
    files.sort(reverse=True)
    return files[0]

def get_worst(dir):
    files = os.listdir(dir)
    files.sort()
    return files[0]
        


def do_validation(model,data_dir,batch_size,input_size):
    model.eval()
    bboxes = []
    images = []
    
    with open(osp.join(data_dir, 'ufo/train.json'), 'r') as f:
        anno = json.load(f)
    image_fnames = sorted(anno['images'].keys())
    for fname in tqdm(image_fnames):
        image = cv2.imread(osp.join(data_dir,"images",fname))[:, :, ::-1]
        images.append(image)
        if len(images) == batch_size:
            bboxes.extend(detect(model, images, input_size))
            images = []

    if len(images):
        bboxes.extend(detect(model, images, input_size))
    pred_dict=dict()
    gt_dict=dict()
    for k, fname in enumerate(image_fnames):
        pred_dict[fname]=bboxes[k].tolist()
        points=[]
        words = anno['images'][fname]['words'].values()
        for word in words:
            points.append(word['points'])
        gt_dict[fname]=points
    score=calc_deteval_metrics(pred_dict,gt_dict)
    return score['total']['precision'],score['total']['recall'],score['total']['hmean']

def main(args):
    do_training(**args.__dict__)


if __name__ == '__main__':
    args = parse_args()
    set_seed(args.seed)
    wandb.login()
    runs=wandb.Api().runs(path="boostcamp_cv13/Data_Preparation",order="created_at")
    this_run_num=f"{int(runs[0].name[1:4])+1:03d}"
    this_run_name=f"[{this_run_num}]-[{args.parent_run_num}]"
    wandb.init(project="Data_Preparation", entity="boostcamp_cv13", name=this_run_name)
    wandb.config.update(args)
    main(args)

