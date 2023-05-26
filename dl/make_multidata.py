import os
import shutil

import cv2
from numpy import imag

"""
Make dataset for multi-task net by combining detection(yolo format) and segmentation(masks) datasets.
"""

# You only need to change this line to your dataset root path
root_path = "/mnt/ext/data/traffic"
if not os.path.exists(root_path):
    print(f"{root_path} is not exist, please check!")
    exit(-1)

images_path = root_path + "/images"
if not os.path.exists(images_path):
    os.makedirs(images_path)

labels_path = root_path + "/labels"
if not os.path.exists(labels_path):
    os.makedirs(labels_path)

masks_path = root_path + "/masks"
if not os.path.exists(masks_path):
    os.makedirs(masks_path)

src_paths = ["det", "seg"]
types = ["train", "val"]

for type in types:
    # source path1
    images_path1 = root_path + f"/{src_paths[0]}/images/{type}"
    if not os.path.exists(images_path1):
        print(f"{images_path1} is not exist, please check!")
        exit(-1)

    labels_path1 = root_path + f"/{src_paths[0]}/labels/{type}"
    if not os.path.exists(labels_path1):
        print(f"{labels_path1} is not exist, please check!")
        exit(-1)

    # source path2
    images_path2 = root_path + f"/{src_paths[1]}/images/{type}"
    if not os.path.exists(images_path2):
        print(f"{images_path2} is not exist, please check!")
        exit(-1)

    masks_path2 = root_path + f"/{src_paths[1]}/masks/{type}"
    if not os.path.exists(masks_path2):
        print(f"{masks_path2} is not exist, please check!")
        exit(-1)

    # destination path
    dst_images_path = images_path + f"/{type}"
    if not os.path.exists(dst_images_path):
        os.makedirs(dst_images_path)

    dst_labels_path = labels_path + f"/{type}"
    if not os.path.exists(dst_labels_path):
        os.makedirs(dst_labels_path)

    dst_masks_path = masks_path + f"/{type}"
    if not os.path.exists(dst_masks_path):
        os.makedirs(dst_masks_path)

    for root, dirs, files in os.walk(images_path1, topdown=True):
        for name in files:

            if not name[-3:]=='jpg':
                continue
            name = name[:-4]

            image_path = os.path.join(images_path2, name + ".jpg")
            label_path = os.path.join(labels_path1, name + ".txt")
            mask_path = os.path.join(masks_path2, name + ".jpg")

            if not os.path.exists(image_path) \
                or not os.path.exists(label_path) \
                or not os.path.exists(mask_path):
                continue

            dst_path = os.path.join(dst_images_path, name + ".jpg")
            print(f"copy {image_path} to {dst_path}")
            shutil.copyfile(image_path, dst_path)

            dst_path = os.path.join(dst_labels_path, name + ".txt")
            print(f"copy {label_path} to {dst_path}")
            shutil.copyfile(label_path, dst_path)

            dst_path = os.path.join(dst_masks_path, name + ".jpg")
            print(f"copy {mask_path} to {dst_path}")
            shutil.copyfile(mask_path, dst_path)

            print()


# # 寻找原图分辨率
# for name in sorted(os.listdir("det/images/val")):
#     path = os.path.join("pictures", name)

#     if os.path.exists(path):
#         print(f"copy {path} to temp/val")
#         os.popen(f"cp -rv {path} temp/val")
#         os.popen("sync")

# # 创建空标签
# labels = sorted(os.listdir("all-traffic/labels/train"))

# for name in sorted(os.listdir("all-traffic/images/train")):
#     name = name.replace(".jpg", ".txt")
#     if name not in labels:
#         path = os.path.join("temp", name)
#         with open(path, "w") as f:
#             print(f"write {path}")

# # 创建空掩图    
# masks = sorted(os.listdir("all-traffic/masks/val"))

# for name in sorted(os.listdir("all-traffic/images/val")):
#     name = name.replace(".jpg", ".jpg")
#     if name not in masks:
#         path = os.path.join("temp", name)
#         img = cv2.imread(os.path.join("all-traffic/images/val", name.replace(".jpg", ".jpg")))
#         mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
#         cv2.imwrite(path, mask)
#         print(f"write {path}")