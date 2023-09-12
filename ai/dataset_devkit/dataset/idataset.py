from typing import List
from abc import ABC, abstractmethod


class Category:
    """
    Category.
    """

    def __init__(self,
                 id: int = -1,
                 name: str = "") -> None:
        self.id = id
        self.name = name


class Image:
    """
    Image.
    """

    def __init__(self,
                 id: int = -1,
                 name: str = "",
                 width: int = 0,
                 height: int = 0) -> None:
        self.id = id
        self.name = name
        self.width = width
        self.height = height


class Annotation:
    """
    Annotation.
    """

    def __init__(self,
                 id: int = -1,
                 img_id: int = -1,
                 cat_id: int = -1) -> None:
        self.id = id
        self.cat_id = cat_id
        self.img_id = img_id


class IDataset(ABC):
    """
    Interface of dataset.
    """

    def __init__(self,
                 root_dir: str,
                 img_dir: str,
                 ann_path: str,
                 img_suffix: str,
                 seg_map_suffix: str) -> None:
        self.root_dir = root_dir
        self.img_dir = img_dir
        self.ann_path = ann_path
        self.img_suffix = img_suffix
        self.seg_map_suffix = seg_map_suffix

        self._create_index()

    @abstractmethod
    def _create_index(self) -> None:
        pass

    @abstractmethod
    def get_cat_ids(self, cat_names: List[str] = []) -> List[int]:
        pass

    @abstractmethod
    def get_img_ids(self, cat_ids: List[int] = []) -> List[int]:
        pass

    @abstractmethod
    def get_ann_ids(self, cat_ids: List[int] = [],
                    img_ids: List[int] = []) -> List[int]:
        pass

    @abstractmethod
    def load_cats(self, cat_ids: List[int] = []) -> List[Category]:
        pass

    @abstractmethod
    def load_imgs(self, img_ids: List[int] = []) -> List[Image]:
        pass

    @abstractmethod
    def load_anns(self, ann_ids: List[int] = []) -> List[Annotation]:
        pass
