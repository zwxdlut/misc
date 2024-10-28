import os
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from mxdataset.mxdataset import LakeStorage  # noqa: E402
from mxdataset.mxdataset import MXDatasetWriter  # noqa: E402
from mxdataset.mxdataset import MXDatasetReader  # noqa: E402
from mxdataset.util import parser_config  # noqa: E402


def branch(args, cfg):
    """
    Branch task.
    """

    lakestore = LakeStorage(
        cfg["lakefs_repo"],
        cfg["lakefs_branch"],
        cfg["lakefs_host"],
        cfg["lakefs_username"],
        cfg["lakefs_password"])

    if args.create:
        lakestore.create_branch(args.create, args.source)
    elif args.delete:
        lakestore.delete_branch(args.delete)
    else:
        bs = lakestore.list_branches()
        if args.list:
            if args.list in bs:
                print("\t", args.list)
        else:
            for b in bs:
                print("\t", b)


def tag(args, cfg):
    """
    Tag task.
    """

    lakestore = LakeStorage(
        cfg["lakefs_repo"],
        cfg["lakefs_branch"],
        cfg["lakefs_host"],
        cfg["lakefs_username"],
        cfg["lakefs_password"])

    if args.create:
        lakestore.create_tag(args.create, args.branch)
    elif args.delete:
        lakestore.delete_tag(args.delete)
    else:
        tags = lakestore.list_tags()
        if args.list:
            if args.list in tags:
                print("\t", args.list)
        else:
            for tag in tags:
                print("\t", tag)


def upload(args, cfg):
    """
    Upload task.
    """

    if args.root_dir:
        root_dir = args.root_dir
    else:
        root_dir = cfg["lakefs_upload_dir"]

    writer = MXDatasetWriter(root_dir, cfg)
    writer.upload2staging(branch=args.branch)
    writer.uploader.close()


def download(args, cfg):
    """
    Download task.
    """

    if args.root_dir:
        root_dir = args.root_dir
    else:
        root_dir = cfg["lakefs_download_dir"]

    if args.branch:
        cfg["lakefs_branch"] = args.branch

    reader = MXDatasetReader(root_dir, cfg)
    reader.download()
    reader.downloader.close()


def object(args, cfg):
    """
    Object task.
    """

    lakestore = LakeStorage(
        cfg["lakefs_repo"],
        cfg["lakefs_branch"],
        cfg["lakefs_host"],
        cfg["lakefs_username"],
        cfg["lakefs_password"])

    if args.delete:
        print("deleting...")
        count = 0
        while True:
            objs = lakestore.list_objects(args.delete, args.prefix)
            lakestore.delete_objects(objs, args.delete)
            # the max amount returned by list is 1000
            count += len(objs)
            if len(objs) < 1000:
                break
        print("{} objects deleted".format(count))
    else:
        objs = lakestore.list_objects(args.list, args.prefix)
        for obj in objs:
            print("\t", obj)
        print(len(objs) + " objects")


def commit(args, cfg):
    lakestore = LakeStorage(
        cfg["lakefs_repo"],
        cfg["lakefs_branch"],
        cfg["lakefs_host"],
        cfg["lakefs_username"],
        cfg["lakefs_password"])
    lakestore.commit(args.msg, args.branch)


def add_branch_parser(subparsers):
    parser_branch = subparsers.add_parser(
        "branch", help="create, delete, list branches")
    parser_branch.add_argument(
        "--create", help="create branch")
    parser_branch.add_argument(
        "--source", help="the source branch from which to create")
    parser_branch.add_argument(
        "--delete", help="delete branch")
    parser_branch.add_argument(
        "--list", help="list a specified branch")


def add_tag_parser(subparsers):
    parser_tag = subparsers.add_parser(
        "tag", help="create, delete, list tags")
    parser_tag.add_argument(
        "--create", help="create tag")
    parser_tag.add_argument(
        "--branch", help="the branch from which to create tag")
    parser_tag.add_argument(
        "--delete", help="delete tag")
    parser_tag.add_argument(
        "--list", help="list a specified tag")


def add_upload_parser(subparsers):
    parser_upload = subparsers.add_parser(
        'upload', help='upload objects')
    parser_upload.add_argument(
        "--root_dir", help="the root directory to upload from")
    parser_upload.add_argument(
        "--branch", help="the branch to which to upload")


def add_download_parser(subparsers):
    parser_download = subparsers.add_parser(
        'download', help='download objects')
    parser_download.add_argument(
        "--root_dir", help="the root directory to which to download")
    parser_download.add_argument(
        "--branch", help="the branch from which to download")


def add_object_parser(subparsers):
    parser_object = subparsers.add_parser(
        "object", help="list, delete objects")
    parser_object.add_argument(
        "--delete", help="delete objects on a branch")
    parser_object.add_argument(
        "--list", help="list objects on a branch")
    parser_object.add_argument(
        "--prefix", default="", help="the prefix for delete or list")


def add_commit_parser(subparsers):
    parser_commit = subparsers.add_parser(
        'commit', help='commit changes')
    parser_commit.add_argument(
        "-m", "--msg", help="the commit message")
    parser_commit.add_argument(
        "--branch", help="the branch to which to commit")


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description='Lakefs tool.')

    # currently only support download files and transform them to mxdataset
    subparsers = parser.add_subparsers(dest='task', help='task parser')
    add_branch_parser(subparsers)
    add_tag_parser(subparsers)
    add_upload_parser(subparsers)
    add_download_parser(subparsers)
    add_object_parser(subparsers)
    add_commit_parser(subparsers)
    args = parser.parse_args()

    return args


def main():
    cfg = parser_config()

    # # debug
    # lakestore = LakeStorage(
    #     cfg["lakefs_repo"],
    #     cfg["lakefs_branch"],
    #     cfg["lakefs_host"],
    #     cfg["lakefs_username"],
    #     cfg["lakefs_password"])
    # lakestore.create_branch("test", "main")
    # bs = lakestore.list_branches()
    # print("branches {}".format(bs))
    # lakestore.delete_branch("test")
    # lakestore.create_tag("test", "main")
    # ts = lakestore.list_tags()
    # print("tags {}".format(ts))
    # lakestore.delete_tag("test")
    # lakestore.upload2stage(
    #     "mxdataset.yaml", f"{project_dir}/config/mxdataset.yaml", "main")
    # lakestore.commit("test", "main")
    # lakestore.download("mxdataset.yaml", "./mxdataset_.yaml", "main")
    # objs = lakestore.list_objects("main", "mxdataset")
    # print("objects: {}".format(objs))
    # lakestore.delete_objects(["mxdataset.yaml"], "main")
    # lakestore.commit("test", "main")
    # os.remove("./mxdataset_.yaml")

    args = parse_args()
    eval(args.task)(args, cfg)


if "__main__" == __name__:
    main()


# EOF
