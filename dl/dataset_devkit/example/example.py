#!/bin/env python3

from dataset import CocoDatasetFactory, VocDatasetFactory

COCO_ROOT_DIR = "/mnt/ext/data/coco/coco"
COCO_IMG_DIR = "/mnt/ext/data/coco/coco/images/train"
COCO_ANN_PATH = "/mnt/ext/data/coco/coco/annotations/instances_train2017.json"

VOC_ROOT_DIR = "/mnt/ext/data/voc/VOCdevkit/VOC2012"
VOC_IMG_DIR = "/mnt/ext/data/voc/VOCdevkit/VOC2012/JPEGImages"
VOC_ANN_PATH = "/mnt/ext/data/voc/VOCdevkit/VOC2012/Annotations"


def main():
    # coco dataset
    root_dir = COCO_ROOT_DIR
    img_dir = COCO_IMG_DIR
    ann_path = COCO_ANN_PATH
    factory = CocoDatasetFactory()
    dataset = factory.create(root_dir, img_dir, ann_path)
    print("Coco dataset ==>>")
    print("cat_ids: {}".format(dataset.get_cat_ids()))

    # voc dataset
    root_dir = VOC_ROOT_DIR
    img_dir = VOC_IMG_DIR
    ann_path = VOC_ANN_PATH
    factory = VocDatasetFactory()
    dataset = factory.create(root_dir, img_dir, ann_path)
    print("Voc dataset ==>> ")
    print("cat_ids: {}".format(dataset.get_cat_ids()))


if "__main__" == __name__:
    main()
