import os
from shutil import copyfile

import cv2

"""
Fuse labes of masks.
"""

SRC_PATH = "/mnt/ext/data/traffic/seg/masks/train"
if not os.path.exists(SRC_PATH):
    print(f"{SRC_PATH} is not exist, please check!")
    exit(0)

DST_PATH = "/mnt/ext/data/traffic/seg/masks/train_out"
if not os.path.exists(DST_PATH):
    os.makedirs(DST_PATH)

LABEL_FILTER = [2, 3, 4, 5, 7, 10, 21]
FIXED_LABEL = 125


for root, dirs, files in os.walk(SRC_PATH, topdown=True):
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

        cv2.imwrite(os.path.join(DST_PATH, name), img)
