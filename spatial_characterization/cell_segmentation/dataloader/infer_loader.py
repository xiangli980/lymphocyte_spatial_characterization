import sys
import math
import numpy as np
import cv2
import matplotlib.pyplot as plt

import torch
import torch.utils.data as data
import staintools
import psutil
import skimage.io as skio

from skimage.morphology import remove_small_objects, dilation, disk
from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu
from skimage.color import rgb2gray, rgb2lab


####
class SerializeFileList(data.IterableDataset):
    """Read a single file as multiple patches of same shape, perform the padding beforehand."""

    def __init__(self, img_list, patch_info_list, patch_size, preproc=None):
        super().__init__()
        self.patch_size = patch_size

        self.img_list = img_list
        self.patch_info_list = patch_info_list

        self.worker_start_img_idx = 0
        # * for internal worker state
        self.curr_img_idx = 0
        self.stop_img_idx = 0
        self.curr_patch_idx = 0
        self.stop_patch_idx = 0
        self.preproc = preproc
        return

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is None:  # single-process data loading, return the full iterator
            self.stop_img_idx = len(self.img_list)
            self.stop_patch_idx = len(self.patch_info_list)
            return self
        else:  # in a worker process so split workload, return a reduced copy of self
            per_worker = len(self.patch_info_list) / float(worker_info.num_workers)
            per_worker = int(math.ceil(per_worker))

            global_curr_patch_idx = worker_info.id * per_worker
            global_stop_patch_idx = global_curr_patch_idx + per_worker
            self.patch_info_list = self.patch_info_list[
                global_curr_patch_idx:global_stop_patch_idx
            ]
            self.curr_patch_idx = 0
            self.stop_patch_idx = len(self.patch_info_list)
            # * check img indexer, implicit protocol in infer.py
            global_curr_img_idx = self.patch_info_list[0][-1]
            global_stop_img_idx = self.patch_info_list[-1][-1] + 1
            self.worker_start_img_idx = global_curr_img_idx
            self.img_list = self.img_list[global_curr_img_idx:global_stop_img_idx]
            self.curr_img_idx = 0
            self.stop_img_idx = len(self.img_list)
            return self  # does it mutate source copy?

    def __next__(self):

        if self.curr_patch_idx >= self.stop_patch_idx:
            raise StopIteration  # when there is nothing more to yield
        patch_info = self.patch_info_list[self.curr_patch_idx]
        img_ptr = self.img_list[patch_info[-1] - self.worker_start_img_idx]
        patch_data = img_ptr[
            patch_info[0] : patch_info[0] + self.patch_size,
            patch_info[1] : patch_info[1] + self.patch_size,
        ]
        self.curr_patch_idx += 1
        if self.preproc is not None:
            patch_data = self.preproc(patch_data)
        return patch_data, patch_info


####


def get_mask(thumb):
    grey = rgb2gray(thumb)
    thresh = threshold_otsu(grey)
    binary = grey < thresh
    binary = dilation(binary, disk(6))
    binary = remove_small_objects(binary, min_size=2000)
    return binary

def get_transformed_image(target, roi):
    
    msk = get_mask(roi)
    # remove small objects
    msk = remove_small_objects(msk.astype('bool'), min_size=20000) # very small objects are likely to be noise

    label_img = label(msk)
    regions = regionprops(label_img)
    for region in regions:
        #labeli = region.label
        bbox = region.bbox
        to_transform = roi[bbox[0]:bbox[2], bbox[1]:bbox[3], :]
        lab = rgb2lab(to_transform)
        if np.sum(lab[:,:,0]<60)<200:  # if the patch is background, skip
            continue
        #print(labeli, bbox)
        #skio.imsave("dataloader/patch_{}.png".format(labeli), to_transform)

        # Stain normalize
        normalizer = staintools.StainNormalizer(method='macenko')
        #normalizer = ReinhardColorNormalizer()
        normalizer.fit(target)
        transformed = normalizer.transform(to_transform)
        roi[bbox[0]:bbox[2], bbox[1]:bbox[3], :] = transformed

    # transform msk into 3 channels
    msk3 = np.zeros((msk.shape[0], msk.shape[1], 3))
    msk3[:,:,0] = msk*1
    msk3[:,:,1] = msk*1
    msk3[:,:,2] = msk*1
    roi[msk3==0] = 255

    return roi

class SerializeArray(data.Dataset):
    def __init__(self, mmap_array_path, patch_info_list, patch_size, preproc=None):
        super().__init__()
        self.patch_size = patch_size
        # use mmap as intermediate sharing, else variable will be duplicated
        # accross torch worker => OOM error, open in read only mode
        self.image = np.load(mmap_array_path, mmap_mode="r")
        # ll = len(patch_info_list)
        # skio.imsave("dataloader/patch_{}.png".format(ll), self.image)
        skio.imsave("dataloader/patch.png", self.image)
        # # Read data
        target = staintools.read_image("dataloader/ref2.png")
        roi = staintools.read_image('dataloader/patch.png')

        # # Standardize brightness (This step is optional but can improve the tissue mask calculation)
        # target = staintools.LuminosityStandardizer.standardize(target)
        # to_transform = staintools.LuminosityStandardizer.standardize(to_transform)

        if np.sum(roi>200)/np.sum(roi>0) <0.98:   # filter out white background
            self.image = get_transformed_image(target, roi)
        else:
            self.image = roi
        #self.image = transformed
        self.patch_info_list = patch_info_list
        self.preproc = preproc
        return

    def __len__(self):
        return len(self.patch_info_list)

    def __getitem__(self, idx):
        patch_info = self.patch_info_list[idx]
        patch_data = self.image[
            patch_info[0] : patch_info[0] + self.patch_size[0],
            patch_info[1] : patch_info[1] + self.patch_size[1],
        ]
       
        if self.preproc is not None:
            patch_data = self.preproc(patch_data)
        return patch_data, patch_info
