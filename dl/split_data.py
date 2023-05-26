import os
import shutil
import random

import cv2
from numpy import imag

"""
Split dataset according proportion.
"""

TRAIN_PROPORTION = 0.9

# You only need to change this line to your dataset root path
root_path = "/mnt/ext/data/traffic"
if not os.path.exists(root_path):
    print(f"{root_path} is not exist, please check!")
    exit(-1)

images_path = root_path + "/images_all"
if not os.path.exists(images_path):
    print(f"{images_path} is not exist, please check!")
    exit(-1)

labels_path = root_path + "/labels_all"
if not os.path.exists(labels_path):
    print(f"{labels_path} is not exist, please check!")
    exit(-1)

masks_path = root_path + "/masks_all"
if not os.path.exists(masks_path):
    print(f"{masks_path} is not exist, please check!")
    exit(-1)

images_train_path = root_path + "/images/train"
if not os.path.exists(images_train_path):
    os.makedirs(images_train_path)

images_val_path = root_path + "/images/val"
if not os.path.exists(images_val_path):
    os.makedirs(images_val_path)

labels_train_path = root_path + "/labels/train"
if not os.path.exists(labels_train_path):
    os.makedirs(labels_train_path)

labels_val_path = root_path + "/labels/val"
if not os.path.exists(labels_val_path):
    os.makedirs(labels_val_path)

masks_train_path = root_path + "/masks/train"
if not os.path.exists(masks_train_path):
    os.makedirs(masks_train_path)

masks_val_path = root_path + "/masks/val"
if not os.path.exists(masks_val_path):
    os.makedirs(masks_val_path)

for root, dirs, files in os.walk(images_path, topdown=True):
    for name in files:

        if not name[-3:]=='jpg':
            continue
        name = name[:-4]

        image_path = os.path.join(images_path, name + ".jpg")
        label_path = os.path.join(labels_path, name + ".txt")
        mask_path = os.path.join(masks_path, name + ".jpg")

        if not os.path.exists(image_path) \
            or not os.path.exists(label_path) \
            or not os.path.exists(mask_path):
            continue

        if random.random() < TRAIN_PROPORTION:
            # dst_path = os.path.join(images_train_path, name + ".jpg")
            print(f"copy {image_path} to {images_train_path}")
            shutil.copy(image_path, images_train_path)

            # dst_path = os.path.join(labels_train_path, name + ".txt")
            print(f"copy {label_path} to {labels_train_path}")
            shutil.copy(label_path, labels_train_path)

            # dst_path = os.path.join(masks_train_path, name + ".jpg")
            print(f"copy {mask_path} to {masks_train_path}")
            shutil.copy(mask_path, masks_train_path)
        else:
            # dst_path = os.path.join(images_val_path, name + ".jpg")
            print(f"copy {image_path} to {images_val_path}")
            shutil.copy(image_path, images_val_path)

            # dst_path = os.path.join(labels_val_path, name + ".txt")
            print(f"copy {label_path} to {labels_val_path}")
            shutil.copy(label_path, labels_val_path)

            # dst_path = os.path.join(masks_val_path, name + ".jpg")
            print(f"copy {mask_path} to {masks_val_path}")
            shutil.copy(mask_path, masks_val_path)
