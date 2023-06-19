import os
from shutil import copyfile

import cv2

"""
Fuse labes of masks.
"""

src_path = "/mnt/ext/data/traffic/seg/masks/train"
if not os.path.exists(src_path):
    print(f"{src_path} is not exist, please check!")
    exit(0)

dst_path = "/mnt/ext/data/traffic/seg/masks/train_out"
if not os.path.exists(dst_path):
    os.makedirs(dst_path)

LABEL_FILTER = [2, 3, 4, 5, 7, 10, 21]
FIXED_LABEL = 125


for root, dirs, files in os.walk(src_path, topdown=True):
    for name in files:

        if not name.endswith(".jpg") and not name.endswith(".png"):
            continue

        img = cv2.imread(os.path.join(root, name), cv2.IMREAD_GRAYSCALE)

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] in LABEL_FILTER:
                    img[i][j] = FIXED_LABEL
                else:
                    img[i][j] = 0

        cv2.imwrite(os.path.join(dst_path, name), img)
