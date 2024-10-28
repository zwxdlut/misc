import os

from mxdataset.imageset import Imageset
from mxdataset.videoset import Videoset
from mxdataset.lakestorage import LakeStorage
from mxdataset.resultset import CreateResultset
from mxdataset.resultset import ReleaseResultset
from mxdataset.mxuploader import MXDatasetUploader
from mxdataset.mxdownloader import MXDatasetDownloader


class MXDatasetReader:
    def __init__(self, root, cfg) -> None:
        self.rootdir = root
        self.lakestore = LakeStorage(
            cfg["lakefs_repo"],
            cfg["lakefs_branch"],
            cfg["lakefs_host"],
            cfg["lakefs_username"],
            cfg["lakefs_password"])
        self.downloader = MXDatasetDownloader(self.rootdir)
        self.resultdir = root + "/resultset/"
        if not os.path.exists(self.resultdir):
            os.makedirs(self.resultdir)
        self.branchroot = root + "/resultset/branches/"
        if not os.path.exists(self.branchroot):
            os.makedirs(self.branchroot)
        self.set_branch(cfg["lakefs_branch"])

    def __del__(self) -> None:
        if self.resultset:
            resultset = self.resultset
            self.resultset = None
            ReleaseResultset(resultset)
        self.lakestore = None

    def set_branch(self, branch, writer=False, download=False):
        if branch is None:
            self.lakestore.setbranch(branch)
            self.viewmode = False
            self.branch = None
            self.branchdir = None
            self.resultset = None
            self.writer = writer
            self.table = None
            return True

        self.viewmode = False
        self.writer = writer
        self.table = None
        self.branch = branch
        self.lakestore.setbranch(branch)
        self.branchdir = self.branchroot + branch + "/"
        if not os.path.exists(self.branchdir):
            os.makedirs(self.branchdir)
        resultpath = self.branchdir + "resultset.db"
        if not os.path.exists(resultpath):
            url = "resultset/resultset.db"
            self.lakestore.download(url, resultpath)
        self.resultset = CreateResultset(resultpath, writer)
        self.downloader.set_resultset(self.resultset)
        self.downloader.set_branch(branch)

        if download and self.resultset:
            self.download()

        return self.resultset is not None

    def list_annotations(self):
        if self.resultset:
            return self.resultset.list_annotations()
        return None

    def create_view(self, view, fromTable, filerSQL):
        if self.writer and self.resultset:
            return self.resultset.create_view(view, fromTable, filerSQL)
        return False

    def pin_annotation(self, ann_cls):
        if self.resultset and (ann_cls in self.list_annotations()):
            self.annotation = self.resultset.get_annotation(ann_cls)
            self.table = self.annotation
            return True
        self.table = None
        return False

    def pin_view(self, view):
        if self.resultset and self.resultset.has_view(view):
            self.viewmode = True
            self.view = self.resultset.get_view(view)
            self.table = self.annotation
            return True
        self.viewmode = False
        self.table = view
        return False

    def pin_table(self, table, isview=False):
        if isview:
            self.pin_view(table)
        else:
            self.pin_annotation(table)

    def get_len(self):
        if self.table:
            return self.table.get_len()
        return 0

    def get_record(self, id):
        if self.table:
            return self.table.get_record(id)
        return None

    def __iter__(self):
        return self.table if self.table else None

    def download(self, timeout=-1):
        self.downloader.download(self.lakestore, timeout)


class MXDatasetWriter:
    def __init__(self, root, cfg) -> None:
        self.rootdir = root
        self.lakestore = LakeStorage(
            cfg["lakefs_repo"],
            cfg["lakefs_branch"],
            cfg["lakefs_host"],
            cfg["lakefs_username"],
            cfg["lakefs_password"])
        self.uploader = MXDatasetUploader(self.rootdir)
        self.imageset = Imageset(root, self.lakestore)
        self.videoset = Videoset(root, self.lakestore)
        self.resultdir = root + "/resultset/"
        self.resultset = CreateResultset(self.resultdir + "resultset.db", True)
        self.uploader.set_resultset(self.resultset)
        if not os.path.exists(self.resultdir):
            raise Exception("Result directory {} not exists!".
                            format(self.resultdir))

    def __del__(self) -> None:
        if self.resultset:
            resultset = self.resultset
            self.resultset = None
            ReleaseResultset(resultset)
        self.lakestore = None
        self.imageset = None
        self.videoset = None

    def set_branch(self, branch=None):
        resultpath = self.resultdir + "resultset.db"
        os.remove(resultpath)
        if branch:
            resulturl = "/resultset/resultset.db"
            self.lakestore.setbranch(branch)
            self.lakestore.upload2stage(resulturl, resultpath)
        self.resultset = CreateResultset(resultpath, True)
        return self.resultset is not None

    def create_view(self, view, fromTable, filerSQL):
        if self.resultset:
            return self.resultset.create_view(view, fromTable, filerSQL)
        return False

    def drop_views(self):
        if self.resultset:
            return self.resultset.drop_views()
        return False

    def create_branch(self, branch, fromBranch):
        self.lakestore.create_branch(branch, fromBranch)

    def upload2staging(self, tables=None, branch=None):
        if branch is None:
            branch = self.lakestore.branch
        if branch is None:
            return False
        if tables is None:
            tables = []
            for ann_cls in self.resultset.list_annotations():
                tables.append((ann_cls, False))
        if len(tables) == 0:
            return False
        self.uploader.upload2staging(self.lakestore, tables, branch)
        self.lakestore.upload2stage(
            "resultset/resultset.db",
            self.resultdir + "resultset.db",
            branch)
        return True

    def commit(self, msg, branch=None):
        if branch is None:
            branch = self.lakestore.branch
        if branch is None:
            return False
        self.lakestore.commit(msg, branch)
        return True


# EOF
