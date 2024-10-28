import os
import json
import time

from pycocotools.coco import COCO

from mxdataset.s3storage import S3Storage
from mxdataset.videoset import Videoset
from mxdataset.imageset import Imageset
from mxdataset.resultset import (CreateResultset, ReleaseResultset,
                                 AnnotationRecord)
from mxdataset.lakestorage import LakeStorage
from mxdataset.util import parser_config

ANN_DET = "detection"
ANN_SEG = "segmentation"


def _get_anns(coco: COCO, img):
    """
    Get annoations from image.
    """

    ann_ids = coco.getAnnIds(imgIds=[img["id"]])
    anns = coco.loadAnns(ann_ids)
    det_anns = []
    seg_anns = []

    for ann in anns:
        if 0 == len(ann[ANN_SEG]):
            det_anns.append(ann)
        else:
            seg_anns.append(ann)

    anns = []
    if 0 != len(det_anns):
        anns.append((
            {
                "cls": ANN_DET,
                "name": img["file_name"].replace(".jpg", ""),
                "suffix": ".json",
            }, det_anns))
    if 0 != len(seg_anns):
        anns.append((
            {
                "cls": ANN_SEG,
                "name": img["file_name"].replace(".jpg", ""),
                "suffix": ".json",
            }, seg_anns))

    return anns


def _add_resultset(resultset, root_dir, ann, img_file):
    ann_dir = os.path.join(root_dir, ann["cls"])
    ann_file = ann["name"] + ann["suffix"]
    img_dir = os.path.join(root_dir, "images")
    table = resultset.get_annotation(ann["cls"])
    record = AnnotationRecord(
        (table.get_lastid() + 1, time.strftime("%Y%m%d", time.localtime()),
            AnnotationRecord.FLAG_VIDEOSET if Videoset.ROOTSUFFIX in root_dir
            else AnnotationRecord.FLAG_IMAGESET, None,
            ann_dir, None, ann_file, img_dir, None, img_file))
    print("[_add_resultset] AnnotationRecord: {}"
          .format(record.make_insertion()))
    table.add_records([record])
    table.flush()


def _transform_files(input_dir, ann_path, output_dir="./output"):
    """
    Transform files to mxdataset.
    dataset format:
    {
        tag_name:
        {
            "images": [image], "anns": [ann], "image_ids": [image_id]
        }
    }
    """

    print("[_transform_files] input_dir: {}, ann_path: {}, output_dir: {}"
          .format(input_dir, ann_path, output_dir))

    dataset = {}
    coco = COCO(ann_path)

    # load images
    img_ids = coco.getImgIds()
    imgs = coco.loadImgs(img_ids)

    # split images
    for img in imgs:
        path = os.path.join(input_dir, img["file_name"])
        if not os.path.exists(path):
            path = os.path.join(input_dir + "/images", img["file_name"])
            if not os.path.exists(path):
                continue
            else:
                input_dir += "/images"

        file = os.path.basename(img["file_name"])
        index = file.rfind("_")

        if -1 == index:
            tag_name = file.split(".")[0]
        else:
            tag_name = file[:index]

        if dataset.get(tag_name) is None:
            dataset[tag_name] = {
                "images": [], "anns": [], "image_ids": []}

        dataset[tag_name]["images"].append(img)
        # TODO: no need anns and image ids in current implementation
        # dataset[tag_name]["image_ids"].append(img["id"])

    # load categories
    cat_ids = coco.getCatIds()
    cats = coco.loadCats(cat_ids)

    # get annoation "info" and "licenses"
    with open(ann_path, "r") as f:
        coco_data = json.load(f)
        if coco_data.get("info") is None:
            coco_data["info"] = {
                "contributor": "",
                "date_created": "",
                "description": "",
                "url": "",
                "version": "",
                "year": ""
            }
        if coco_data.get("licenses") is None:
            coco_data["licenses"] = [
                {
                    "name": "",
                    "id": 0,
                    "url": ""
                }
            ]

    lakestore = LakeStorage()
    videoset = Videoset(output_dir, lakestore)
    imageset = Imageset(output_dir, lakestore)

    path = output_dir + "/resultset"
    if not os.path.exists(path):
        os.makedirs(path)

    path += "/resultset.db"
    resultset = CreateResultset(path, True)
    resultset.create_annotation(ANN_DET)
    resultset.create_annotation(ANN_SEG)

    # write images and and annoations
    for i in dataset:
        vfpath = None

        for img in dataset[i]["images"]:
            path = os.path.join(input_dir, img["file_name"])
            if not os.path.exists(path):
                print("[_transform_files] image {} isn't exists!"
                      .format(path))
                continue

            with open(path, "rb") as f:
                data = {
                    'info': coco_data["info"],
                    'licenses': coco_data["licenses"],
                    'categories': cats,
                }

                try:
                    # add image
                    print("[_transform_files] add image {}"
                          .format(img["file_name"]))
                    file = os.path.basename(img["file_name"])
                    vfpath = videoset.add_image(file, f)
                    img["file_name"] = vfpath.frame
                    data["images"] = [img]

                    # add annoation
                    anns = _get_anns(coco, img)
                    for ann, content in anns:
                        # add videoset
                        data["annotations"] = content
                        bytes = json.dumps(data).encode("utf-8")
                        vfdir = vfpath.get_dir()
                        print("[_transform_files] add videoset annoation, "
                              "vfdir: {}, ann: {}"
                              .format(vfdir, ann))
                        vfpath = videoset.add_annotation(vfpath, ann, bytes)

                        # add resultset
                        print("[_transform_files] add resultset")
                        _add_resultset(
                            resultset, Videoset.ROOTSUFFIX + "/" + vfdir,
                            ann, vfpath.frame)

                except Exception as e:
                    # vfpath is invalid or other exception
                    # add image to imageset
                    print(e)

                    # add image
                    imageset.add_image(file, f)
                    img["file_name"] = file
                    data["images"] = [img]

                    # add annoation
                    anns = _get_anns(coco, img)
                    for ann, content in anns:
                        # add imageset
                        data["annotations"] = content
                        bytes = json.dumps(data).encode("utf-8")
                        print("[_transform_files] add imageset annoation"
                              "ann: {}".format(ann))
                        imageset.add_annotation(ann, bytes)

                        # add resultset
                        print("[_transform_files] add resultset")
                        _add_resultset(
                            resultset, Imageset.ROOTSUFFIX,
                            ann, img["file_name"])

    resultset.flush()
    ReleaseResultset(resultset)

    return True


def download_files(url, access_key_id, secrect_access_key,
                   bucket=None, prefix="", dst_dir="./download"):
    """
    Download files.
    """

    s3store = S3Storage(url, access_key_id, secrect_access_key)

    # get buckets
    buckets = s3store.get_buckets(bucket)
    print("[download_files] len: {} | buckets: {}"
          .format(len(buckets), buckets))

    # # get files
    # for bucket in buckets:
    #     print("[download_files] bucket: {}, prefix: {}"
    #           .format(bucket['Name'], prefix))
    #     files = s3store.get_files(bucket["Name"], prefix)
    #     print("[download_files] get {} files".format(len(files)))

    # download files
    for bucket in buckets:
        print("[download_files] bucket: {}, prefix: {}, dst_dir: {}"
              .format(bucket['Name'], prefix, dst_dir))
        s3store.download_objects(bucket["Name"], prefix, dst_dir)

    return True


def transform_files(input_dir, output_dir="./output"):
    """
    Transform annotation files to mxdataset.
    """

    if not os.path.exists(input_dir):
        print("[transform_files] input directory {} isn't exists!".
              format(input_dir))
        return False

    for root, dirs, files in os.walk(input_dir, topdown=True):
        for file in files:
            if not file.endswith(".json"):
                continue

            ann_path = os.path.join(root, file)

            with open(ann_path, "r") as f:
                dataset = json.load(f)

                if 'annotations' not in dataset \
                        or 'images' not in dataset \
                        or 'categories' not in dataset \
                        or 'annotations' not in dataset:
                    print("[transform_files] {} invalid!".format(ann_path))
                    continue

            _transform_files(input_dir, ann_path, output_dir)

    return True


def migrate():
    """
    Migrate annotation files to mxdataset.
    """

    cfg = parser_config()
    print("[migrate] config >> \n{}".format(cfg))

    download_files(
        url=cfg["s3_url"],
        access_key_id=cfg["s3_access_key_id"],
        secrect_access_key=cfg["s3_secret_access_key"],
        bucket=cfg["bucket"],
        prefix=cfg["prefix"],
        dst_dir=cfg["migration_download_dir"])

    for dir in os.listdir(cfg["migration_download_dir"]):
        download_dir = os.path.join(cfg["migration_download_dir"], dir)
        if not os.path.isdir(download_dir):
            continue

        transform_files(
            input_dir=download_dir,
            output_dir=cfg["migration_destination_dir"])

    return True


# EOF
