import os

from mxdataset import fileset


# Imageset manages Imageset db. Used only for writing!
class Imageset():
    ROOTSUFFIX = "imageset"
    FILEMXCNT = 500
    UPLOADBATCHSIZE = 100
    UPLOADTABLE = "uploaded"

    def __init__(self, dbroot, lakestore) -> None:
        self.rootdir = dbroot + "/" + Imageset.ROOTSUFFIX
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir)
        self.fileset = fileset.Fileset(self.rootdir + "/fileset.db")
        self.files = {
            fileset.Fileset.IMG_TABLE: [],
            fileset.Fileset.DET_ANN_TABLE: [],
            fileset.Fileset.SEG_ANN_TABLE: []
        }
        self.lakestore = lakestore

        imgdir = self.rootdir + "/images/"
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)

    def __del__(self) -> None:
        self.flush()
        self.fileset = None

    def add_image(self, img, data):
        relpath = "images/" + img
        fullpath = os.path.join(self.rootdir, relpath)
        fulldir = os.path.dirname(fullpath)
        if not os.path.exists(fulldir):
            os.makedirs(fulldir)

        self.add_file(relpath, fileset.Fileset.IMG_TABLE)

        file = open(fullpath, "wb")
        if isinstance(data, bytes):
            file.write(data)
        else:
            file.write(data.read())
        file.close()

        return True

    def add_annotation(self, ann, data):
        relpath = ann["cls"] + "/" + ann["name"] + ann["suffix"]
        fullpath = os.path.join(self.rootdir, relpath)
        fulldir = os.path.dirname(fullpath)
        if not os.path.exists(fulldir):
            os.mkdir(fulldir)

        self.add_file(relpath, fileset.Fileset.DET_ANN_TABLE
                      if "detection" == ann["cls"]
                      else fileset.Fileset.SEG_ANN_TABLE)

        file = open(fullpath, "wb")
        if isinstance(data, bytes):
            file.write(data)
        else:
            file.write(data.read())
        file.close()

        return True

    def upload2staging(self):
        self.flush()

        table = Imageset.UPLOADTABLE
        batchsize = Imageset.UPLOADBATCHSIZE
        if not self.fileset.has_table(table):
            self.fileset.create_table(table)
        need_upload_cnt = self.fileset.get_len(fileset.Fileset.IMG_TABLE) \
            + self.fileset.get_len(fileset.Fileset.DET_ANN_TABLE) \
            + self.fileset.get_len(fileset.Fileset.SEG_ANN_TABLE)
        need_upload_cnt -= self.fileset.get_len(table)
        batch_upload_cnt = need_upload_cnt // batchsize
        need_upload_cnt = need_upload_cnt % batchsize

        lastid = self.fileset.get_lastid(table)
        while batch_upload_cnt > 0:
            self.batch_upload2staging(self, lastid, batchsize)
            lastid += batchsize
        if need_upload_cnt > 0:
            self.batch_upload2staging(self, lastid, need_upload_cnt)
            lastid += need_upload_cnt
        if not self.check_upload():
            raise Exception("Check upload failed!")

    def batch_upload2staging(self, lastid, batchsize):
        upload_files = []
        for i in range(batchsize):
            id = lastid + i
            relpath = self.fileset.get_file(id)
            fullpath = self.rootdir + relpath
            self.lakestore.upload2staging(relpath, fullpath)
            upload_files.append(relpath)
        self.fileset.add_files(upload_files, Imageset.UPLOADTABLE)

    def check_upload(self):
        len = self.fileset.get_len(fileset.Fileset.IMG_TABLE) \
            + self.fileset.get_len(fileset.Fileset.DET_ANN_TABLE) \
            + self.fileset.get_len(fileset.Fileset.SEG_ANN_TABLE)
        table = Imageset.UPLOADTABLE
        if not self.fileset.has_table(table):
            return (len == 0)

        need_upload_cnt = len
        need_upload_cnt -= self.fileset.get_len(table)
        if need_upload_cnt > 0:
            return False

        return True

    def add_file(self, relpath, table):
        self.files[table].append(relpath)
        if len(self.files[table]) > Imageset.FILEMXCNT:
            self.fileset.add_files(self.files[table], table)
            self.files[table] = []

    def flush(self):
        for table, files in self.files.items():
            if len(files) > 0:
                self.fileset.add_files(files, table)
                self.files[table] = []
        self.fileset.flush()


# EOF
