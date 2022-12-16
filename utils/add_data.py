##requiremetns install
#pip install gdown

## import library
from argparse import ArgumentParser
import gdown
import os
import glob
import zipfile
import shutil

##boolean parsing
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
## parser
def parse_args():
    parser = ArgumentParser()

    # Conventional args
    parser.add_argument('--file_id', type=str, default='1EsCTJ7K47BgOMiVxZFu38m6m4-NBUMnv')
    parser.add_argument('--output_dir', type=str, default='../input/data/custom/')
    parser.add_argument('--output_file_name', type=str, default='data.zip')
    parser.add_argument('--download_option', type=str2bool, default=True)
    parser.add_argument('--decompress_option', type=str2bool, default=True)
    parser.add_argument('--erase_images', type=str2bool, default=False)
    
    args = parser.parse_args()
    
    return args

##drive download
def download_gdrive(file_id, output_name, output_dir):
    google_path = 'https://drive.google.com/uc?id='
    gdown.download(google_path + file_id, output_dir + output_name, quiet = False)

#decompress zip file
def decompress(output_name, output_dir):
    zipfile.ZipFile(output_dir + output_name).extractall(path= output_dir + 'images/')
    ann_name = 'annotation.json'
    dir = output_dir + 'ufo/'
    shutil.move(output_dir + 'images/' + ann_name, dir + ann_name )
#erase image data    
def erase(output_dir):
    [os.remove(f) for f in glob.glob(output_dir+"*.JPG")]
    [os.remove(f) for f in glob.glob(output_dir+"*.jpg")]
    [os.remove(f) for f in glob.glob(output_dir+"*.jpeg")]
    
def main(args):
    if args.download_option == True:
        download_gdrive(args.file_id, args.output_file_name, args.output_dir)
    if args.decompress_option == True:
        decompress(args.output_file_name, args.output_dir)
    if args.erase_images:
        erase(args.output_dir)


if __name__ == '__main__':
    args = parse_args()
    main(args)