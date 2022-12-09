import json
import os
import os.path as osp
from glob import glob
from PIL import Image

import numpy as np
from tqdm import tqdm

from torch.utils.data import DataLoader, ConcatDataset, Dataset


SRC_DATASET_DIR = '/opt/ml/input/data'  # FIXME
DST_DATASET_DIR = '/opt/ml/input/data'  # FIXME

NUM_WORKERS = 32  # FIXME

IMAGE_EXTENSIONS = {'.gif', '.jpg', '.png'}

LANGUAGE_MAP = {
    'Korean': 'ko',
    'Latin': 'en',
    'Symbols': None
}

def get_language_token(x):
    return LANGUAGE_MAP.get(x, 'others')


def maybe_mkdir(x):
    if not osp.exists(x):
        os.makedirs(x)


class MLT17Dataset(Dataset):
    def __init__(self, source_dir, image_dir, label_dir, copy_images_to=None):
        self.image_dir = image_dir
        new_image_dir = osp.join(source_dir, image_dir)
        new_image_dir = osp.join(new_image_dir, 'images')
        image_paths = {x for x in glob(osp.join(new_image_dir, '*')) if osp.splitext(x)[1] in
                       IMAGE_EXTENSIONS}
        label_paths = set(glob(osp.join(label_dir, '*.txt')))
        assert len(image_paths) == len(label_paths)

        sample_ids, samples_info = list(), dict()
        for image_path in image_paths:
            sample_id = osp.splitext(osp.basename(image_path))[0]
            label_path = osp.join(label_dir, 'gt_{}.txt'.format(sample_id))
            assert label_path in label_paths

            words_info, extra_info = self.parse_label_file(label_path)
            if 'ko' not in extra_info['languages'] and 'en' not in extra_info['languages']:
                continue

            sample_ids.append(sample_id)
            samples_info[sample_id] = dict(image_path=image_path, label_path=label_path,
                                           words_info=words_info)

        self.sample_ids, self.samples_info = sample_ids, samples_info

        self.copy_images_to = copy_images_to

    def __len__(self):
        return len(self.sample_ids)

    def __getitem__(self, idx):
        sample_info = self.samples_info[self.sample_ids[idx]]

        image_fname = osp.basename(sample_info['image_path'])
        image = Image.open(sample_info['image_path'])
        img_w, img_h = image.size

        if self.copy_images_to:
            maybe_mkdir(self.copy_images_to)
            image.save(osp.join(self.copy_images_to, osp.basename(sample_info['image_path'])))

        license_tag = dict(usability=True, public=True, commercial=True, type='CC-BY-SA',
                           holder=None)
        sample_info_ufo = dict(img_h=img_h, img_w=img_w, words=sample_info['words_info'], tags=None,
                               license_tag=license_tag)
                               
        image_path = self.image_dir + '/images/' + image_fname

        return image_path, sample_info_ufo

    def parse_label_file(self, label_path):
        def rearrange_points(points):
            start_idx = np.argmin([np.linalg.norm(p, ord=1) for p in points])
            if start_idx != 0:
                points = np.roll(points, -start_idx, axis=0).tolist()
            return points

        with open(label_path, encoding='utf-8') as f:
            lines = f.readlines()

        words_info, languages = dict(), set()
        for word_idx, line in enumerate(lines):
            items = line.strip().split(',', 9)
            language, transcription = items[8], items[9]
            points = np.array(items[:8], dtype=np.float32).reshape(4, 2).tolist()
            points = rearrange_points(points)
            orientation = 'Horizontal'
            language = get_language_token(language)
            illegibility = True if (language != 'en' and language != 'ko') or transcription == '###' else False
            words_info[word_idx] = dict(
                points=points, transcription=transcription, language=[language],
                illegibility=illegibility, orientation=orientation, word_tags=None
            )
            languages.add(language)

        return words_info, dict(languages=languages)

class MLT15Dataset(Dataset):
    def __init__(self, source_dir, image_dir, label_dir, copy_images_to=None):
        self.image_dir = image_dir
        new_image_dir = osp.join(source_dir, image_dir)
        new_image_dir = osp.join(new_image_dir, 'images')
        image_paths = {x for x in glob(osp.join(new_image_dir, '*')) if osp.splitext(x)[1] in
                       IMAGE_EXTENSIONS}
        label_paths = set(glob(osp.join(label_dir, '*.txt')))
        assert len(image_paths) == len(label_paths)

        sample_ids, samples_info = list(), dict()
        for image_path in image_paths:
            sample_id = osp.splitext(osp.basename(image_path))[0]

            label_path = osp.join(label_dir, 'gt_{}.txt'.format(sample_id))
            assert label_path in label_paths

            words_info, extra_info = self.parse_label_file(label_path)
            # if extra_info['languages'].difference({'ko', 'en'}):
            #     continue

            sample_ids.append(sample_id)
            samples_info[sample_id] = dict(image_path=image_path, label_path=label_path,
                                           words_info=words_info)

        self.sample_ids, self.samples_info = sample_ids, samples_info

        self.copy_images_to = copy_images_to

    def __len__(self):
        return len(self.sample_ids)

    def __getitem__(self, idx):
        sample_info = self.samples_info[self.sample_ids[idx]]

        image_fname = osp.basename(sample_info['image_path'])
        image = Image.open(sample_info['image_path'])
        img_w, img_h = image.size

        if self.copy_images_to:
            maybe_mkdir(self.copy_images_to)
            image.save(osp.join(self.copy_images_to, osp.basename(sample_info['image_path'])))

        license_tag = dict(usability=True, public=True, commercial=True, type='CC-BY-SA',
                           holder=None)
        sample_info_ufo = dict(img_h=img_h, img_w=img_w, words=sample_info['words_info'], tags=None,
                               license_tag=license_tag)
        
        image_path = self.image_dir + '/images/' + image_fname

        return image_path, sample_info_ufo

    def parse_label_file(self, label_path):
        def rearrange_points(points):
            start_idx = np.argmin([np.linalg.norm(p, ord=1) for p in points])
            if start_idx != 0:
                points = np.roll(points, -start_idx, axis=0).tolist()
            return points

        with open(label_path, encoding='utf-8-sig') as f:
            lines = f.readlines()

        words_info, languages = dict(), set()
        for word_idx, line in enumerate(lines):
            items = line.strip().split(',', 8)
            transcription = items[-1]
            points = np.array(items[:8], dtype=np.float32).reshape(4, 2).tolist()
            points = rearrange_points(points)

            illegibility = transcription == '###'
            orientation = 'Horizontal'
            language = 'en'
            words_info[word_idx] = dict(
                points=points, transcription=transcription, language=[language],
                illegibility=illegibility, orientation=orientation, word_tags=None
            )
            languages.add(language)

        return words_info, dict(languages=languages)


def main():
    dst_image_dir = osp.join(DST_DATASET_DIR, 'images')
    # dst_image_dir = None

    mlt_train = MLT17Dataset(SRC_DATASET_DIR, 'ICDAR17_val',
                             osp.join(SRC_DATASET_DIR, 'ICDAR17_val/ICDAR2017-gt_val'),
                             copy_images_to=None)
    mlt_valid = MLT15Dataset(SRC_DATASET_DIR, 'ICDAR15',
                             osp.join(SRC_DATASET_DIR, 'ICDAR15/ICDAR15-gt'),
                             copy_images_to=None)
    mlt_merged = ConcatDataset([mlt_train, mlt_valid])

    anno = dict(images=dict())
    with tqdm(total=len(mlt_merged)) as pbar:
        for batch in DataLoader(mlt_merged, num_workers=NUM_WORKERS, collate_fn=lambda x: x):
            image_fname, sample_info = batch[0]
            anno['images'][image_fname] = sample_info
            pbar.update(1)

    ufo_dir = osp.join(DST_DATASET_DIR, 'ufo')
    maybe_mkdir(ufo_dir)
    with open(osp.join(ufo_dir, 'train.json'), 'w') as f:
        json.dump(anno, f, indent=4)


if __name__ == '__main__':
    main()
