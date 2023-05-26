import os
from shutil import copyfile

import cv2
from numpy import imag
from numba import jit
import random
import torch

"""
Fuse labes of masks.
"""

# You only need to change this line to your dataset root path
src_path = "/mnt/ext/data/traffic_all/seg/masks/train"
if not os.path.exists(src_path):
    print(f"{src_path} is not exist, please check!")
    exit(0)

dst_path = "/mnt/ext/data/traffic_all/seg/masks/train_out"
if not os.path.exists(dst_path):
    os.makedirs(dst_path)

k = 0
FUSE_FILTER = [2, 3, 4, 5, 7, 10, 21]

for root, dirs, files in os.walk(src_path, topdown=True):
    for name in files:

        if not name[-3:]=='jpg' and not name[-3:]=='png':
            continue

        img = cv2.imread(os.path.join(src_path, name), cv2.IMREAD_GRAYSCALE)

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] in FUSE_FILTER:
                    img[i][j] = 125
                else:
                    img[i][j] = 0

        cv2.imwrite(os.path.join(dst_path, name), img)
        k += 1

        if k > 10:
            break

