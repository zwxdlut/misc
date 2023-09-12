# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package
import unittest
from dataset import CocoDatasetFactory, VocDatasetFactory

COCO_ROOT_DIR = "/mnt/ext/data/coco/coco"
COCO_IMG_DIR = "/mnt/ext/data/coco/coco/images/train"
COCO_ANN_PATH = "/mnt/ext/data/coco/coco/annotations/instances_train2017.json"

VOC_ROOT_DIR = "/mnt/ext/data/voc/VOCdevkit/VOC2012"
VOC_IMG_DIR = "/mnt/ext/data/voc/VOCdevkit/VOC2012/JPEGImages"
VOC_ANN_PATH = "/mnt/ext/data/voc/VOCdevkit/VOC2012/Annotations"


class TestDataset(unittest.TestCase):
    def test_coco_dataset(self):
        root_dir = COCO_ROOT_DIR
        img_dir = COCO_IMG_DIR
        ann_path = COCO_ANN_PATH
        factory = CocoDatasetFactory()
        dataset = factory.create(root_dir, img_dir, ann_path)
        self.assertTrue(dataset)

    def test_voc_dataset(self):
        root_dir = VOC_ROOT_DIR
        img_dir = VOC_IMG_DIR
        ann_path = VOC_ANN_PATH
        factory = VocDatasetFactory()
        dataset = factory.create(root_dir, img_dir, ann_path)
        self.assertTrue(dataset)


if '__main__' == __name__:
    unittest.main()
