from abc import ABC, abstractmethod

from .idataset import IDataset
from .coco_dataset import CocoDataset
from .voc_dataset import VocDataset


class IDatasetFactory(ABC):
    """
    Interface of dataset metadata factory.
    """

    @abstractmethod
    def create(self,
               root_dir: str,
               img_dir: str,
               ann_path: str,
               img_suffix=".jpg",
               seg_map_suffix=".png") -> IDataset:
        pass


class CocoDatasetFactory(IDatasetFactory):
    """
    Coco dataset factory.
    """

    def create(self,
               root_dir: str,
               img_dir: str,
               ann_path: str,
               img_suffix=".jpg",
               seg_map_suffix=".png") -> IDataset:
        return CocoDataset(root_dir,
                           img_dir,
                           ann_path,
                           img_suffix,
                           seg_map_suffix)


class VocDatasetFactory(IDatasetFactory):
    """
    Voc dataset factory.
    """

    def create(self,
               root_dir: str,
               img_dir: str,
               ann_path: str,
               img_suffix=".jpg",
               seg_map_suffix=".png") -> IDataset:
        return VocDataset(root_dir,
                          img_dir,
                          ann_path,
                          img_suffix,
                          seg_map_suffix)
