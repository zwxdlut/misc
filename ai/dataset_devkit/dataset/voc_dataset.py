from typing import List

from .idataset import Category, Image, Annotation, IDataset


class VocDataset(IDataset):
    """
    Voc dataset.
    """

    def __init__(self,
                 root_dir: str,
                 img_dir: str,
                 ann_path: str,
                 img_suffix: str = ".jpg",
                 seg_map_suffix: str = ".png") -> None:
        super(VocDataset, self).__init__(
            root_dir, img_dir, ann_path, img_suffix, seg_map_suffix)

    def _create_index(self) -> None:
        pass

    def get_cat_ids(self, cat_names: List[str] = []) -> List[int]:
        pass

    def get_img_ids(self, cat_ids: List[int] = []) -> List[int]:
        pass

    def get_ann_ids(self, cat_ids: List[int] = [],
                    img_ids: List[int] = []) -> List[int]:
        pass

    def load_cats(self, cat_ids: List[int] = []) -> List[Category]:
        pass

    def load_imgs(self, img_ids: List[int] = []) -> List[Image]:
        pass

    def load_anns(self, ann_ids: List[int] = []) -> List[Annotation]:
        pass
