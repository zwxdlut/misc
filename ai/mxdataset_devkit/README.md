# Mxdataset Devkit

This devkit makes and manages mxdataset.

- mxdataset
   - imageset
      - images
         - [annotation task 0]
   - videoset
      - [path of video 0]
         - images
            - [annotation task 0]
   - resultset
      - resultset.db
      - branch
         - [branch 0]

Version management:

1. Use lakefs branch to manage different verision.
2. Version id is defined by date: 20230210.
3. Lakefs version example: 20230208-->20230210-->[20230211|main].

## Prerequisites

```
sudo apt install awscli
aws configure # configure your aws
```

## Installation

### Best Practices

```
tox
pip install dist/mxdataset-xxx
```

### Verify the installation

```
python
import mxdataset
```

## Usage

### Migration

Migrate images and annotation files to mxdataset.

```
python tools/migration.py
```

The excution parameters are configured in mxdataset.yaml. This has two steps: download; transform. You can run it step by step.

**1. Download**

Download images and annotation files from s3 storage.

```
python tools/migration.py download [--bucket ${BUCKET_NAME}] [--prefix ${PATH_PREFIX}] [--dst_dir ${DST_DIR}]
```

- --bucket: the bucket to download from, None for migrating all buckets
- --prefix: the path prefix to filter, "" for migrating all objects
- --dst_dir: the destination directory

**2. Transform**

Transform the images and annotation files to mxdataset.

```
python tools/migration.py transform ${--input_dir {INPUT_DIR}} [--output_dir ${OUTPUT_DIR}]
```

- --input_dir: the input directory
- --output_dir: the output directory

If the parameters are not provided, that in mxdataset.yaml will be used.

### Databse management

Manage mxdataset by lakefs.

**Branch**

Create branch.

```
python tools/mxlakefs.py branch [--create ${BRANCH_NAME}] [--source ${SOURCE_BRANCH}]
```

- --create: the branch to create
- --source: the source branch from which to create, if not specified, it will use that in config file "mxdataset.yaml"

Delete branch.

```
python tools/mxlakefs.py branch [--delete ${BRANCH_NAME}]
```

- --delete: the branch to delete

List branches.

```
python tools/mxlakefs.py branch [--list ${BRANCH_NAME}]
```

- --list: the branch to list or list all branches without --list.

**Tag**

Create tag.

```
python tools/mxlakefs.py tag [--create ${TAG_NAME}] [--branch ${BRANCH_NAME}]
```

- --create: the tag to create
- --branch: the branch from which to create tag, if not specified, it will use that in config file "mxdataset.yaml"

Delete tag.

```
python tools/mxlakefs.py tag [--delete ${TAG_NAME}]
```

- --delete: the tag to delete

List tags.

```
python tools/mxlakefs.py tag [--list ${TAG_NAME}]
```

- --list: the tag to list or list all tags without --list.

**Upload**

```
python tools/mxlakefs.py upload [--root_dir ${ROOT_DIR}] [--branch ${BRANCH_NAME}]
```

- --root_dir: the root directory from which to upload
- --branch: the branch to which to upload

If the parameters above are not specified, it will use those in the config file "mxdataset.yaml".

**Download**

```
python tools/mxlakefs.py download [--root_dir ${ROOT_DIR}] [--branch ${BRANCH_NAME}]
```

- --root_dir: the root directory to which to download
- --branch: the branch from which to download

If the parameters above are not specified, it will use those in the config file "mxdataset.yaml".

**Object**

Delete objects.

```
python tools/mxlakefs.py object [--delete ${BRANCH_NAME}] [--prefix ${PATH_PREFIX}]
```

- --delete: the branch on which to delete objects
- --prefix: the path prefix to delete, default is ""

List objects.

```
python tools/mxlakefs.py object [--list ${BRANCH_NAME}] [--prefix ${PATH_PREFIX}]
```

- --list: the branch on which to list objects, if not specified, it will use that in config file "mxdataset.yaml"
- --prefix: the path prefix to list, default is ""

**Commit**

```
python tools/mxlakefs.py commit -m ${MSG} [--branch ${BRANCH_NAME}]
```

- -m, --msg: the commit message
- --branch: the branch to which to commit, if not specified, it will use that in config file "mxdataset.yaml"

## Author
* Wenxing Zhang zwxdlut@163.com

## License
* Licensed under the GPLv3 license.
