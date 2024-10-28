import os
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from mxdataset.migration.migration import migrate  # noqa: E402
from mxdataset.migration.migration import download_files  # noqa: E402
from mxdataset.migration.migration import transform_files  # noqa: E402
from mxdataset.util import parser_config  # noqa: E402


def download(args):
    """
    Download task.
    """

    cfg = parser_config()

    if args.bucket is not None:
        bucket = args.bucket
    else:
        bucket = cfg["bucket"]

    if args.prefix is not None:
        prefix = args.prefix
    else:
        prefix = cfg["prefix"]

    if args.dst_dir is not None:
        dst_dir = args.dst_dir
    else:
        dst_dir = cfg["migration_download_dir"]

    download_files(
        cfg["s3_url"], cfg["s3_access_key_id"], cfg["s3_secret_access_key"],
        bucket, prefix, dst_dir)


def transform(args):
    """
    Transform task.
    """

    cfg = parser_config()

    if args.input_dir is not None:
        input_dir = args.input_dir
    else:
        input_dir = cfg["migration_download_dir"]

    if args.output_dir is not None:
        output_dir = args.output_dir
    else:
        output_dir = cfg["migration_destination_dir"]

    for dir in os.listdir(input_dir):
        sub_dir = os.path.join(input_dir, dir)
        if not os.path.isdir(sub_dir):
            continue

        transform_files(sub_dir, output_dir)


def add_download_parser(subparsers):
    parser_download = subparsers.add_parser(
        "download", help="download images and annotation files")
    parser_download.add_argument(
        "--bucket", help="the bucket to download from")
    parser_download.add_argument(
        "--prefix", help="the path prefix to filter")
    parser_download.add_argument(
        "--dst_dir", help="the destination directory")


def add_transform_parser(subparsers):
    parser_transform = subparsers.add_parser(
        'transform', help='tansform images and annotation files to mxdataset')
    parser_transform.add_argument(
        "--input_dir", help="the input directory")
    parser_transform.add_argument(
        "--output_dir", help="the output directory")


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrate images and annotation files to mxdataset.')

    # currently only support download images and
    # annotation files and transform them to mxdataset
    subparsers = parser.add_subparsers(dest='task', help='the task parser')
    add_download_parser(subparsers)
    add_transform_parser(subparsers)
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    if args.task is None:
        migrate()
    else:
        eval(args.task)(args)


if "__main__" == __name__:
    main()


# EOF
