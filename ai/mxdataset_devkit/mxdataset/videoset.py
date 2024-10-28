import os
import sqlite3
from pathlib import Path
from mxdataset import fileset


# Videoset manages videoset db. Used only for writing!
class Videoset():
    ROOTSUFFIX = "videoset"
    VIDEOMAXCNT = 50
    FILEMXCNT = 500
    UPLOADBATCHSIZE = 100
    UPLOADTABLE = "uploaded"

    def __init__(self, dbroot, lakestore) -> None:
        self.rootdir = dbroot + "/" + Videoset.ROOTSUFFIX
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir)
        self.videoset = None
        self.fileset = fileset.Fileset(self.rootdir + "/fileset.db")
        self.files = {
            fileset.Fileset.IMG_TABLE: [],
            fileset.Fileset.DET_ANN_TABLE: [],
            fileset.Fileset.SEG_ANN_TABLE: []
        }
        self.lakestore = lakestore
        self.videorelpath = Videoset.ROOTSUFFIX + "/videoset.db"
        self.videopath = self.rootdir + "/videoset.db"
        self.videos = []
        self.videoset_changed = False

        # TODO: for what
        # if self.lakestore.branch:
        #     self.init_vtable()

    def __del__(self) -> None:
        self.flush()

    def init_vtable(self):
        self.lakestore.download(self.videorelpath, self.videopath)
        self.videoset = VideosetTable(self.videopath)

    def add_image(self, img, data):
        vfpath = VideoFilePath(img, False, True)
        if not vfpath.valid:
            err = "video file path " + img + " not valid!"
            raise Exception(err)
        vdir = vfpath.get_dir()
        relpath = vdir + "/images/" + vfpath.frame
        fullpath = os.path.join(self.rootdir, relpath)
        fulldir = os.path.dirname(fullpath)
        if not os.path.exists(fulldir):
            os.makedirs(fulldir)
            self.add_video(vdir)

        self.add_file(relpath, fileset.Fileset.IMG_TABLE)

        file = open(fullpath, "wb")
        if isinstance(data, bytes):
            file.write(data)
        else:
            file.write(data.read())
        file.close()

        return vfpath

    def add_annotation(self, vfpath, ann, data):
        if not vfpath.valid:
            err = "video file " + vfpath.get_file() + " not valid!"
            raise Exception(err)
        vdir = vfpath.get_dir()
        # relpath = vdir + "/" + ann["cls"] + "/"
        # relpath += vfpath.frame.replace(".jpg", ann["suffix"])
        relpath = vdir + "/" + ann["cls"] + "/" + ann["name"] + ann["suffix"]
        fullpath = os.path.join(self.rootdir, relpath)
        fulldir = os.path.dirname(fullpath)
        if not os.path.exists(fulldir):
            # err = "directory " + fulldir + " not exist!"
            # raise Exception(err)
            os.makedirs(fulldir)

        self.add_file(relpath, fileset.Fileset.DET_ANN_TABLE
                      if "detection" == ann["cls"]
                      else fileset.Fileset.SEG_ANN_TABLE)

        file = open(fullpath, "wb")
        if isinstance(data, bytes):
            file.write(data)
        else:
            file.write(data.read())
        file.close()

        return vfpath

    def upload2staging(self):
        self.flush()

        table = Videoset.UPLOADTABLE
        batchsize = Videoset.UPLOADBATCHSIZE
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
        self.fileset.add_files(upload_files, Videoset.UPLOADTABLE)

    def check_upload(self):
        len = self.fileset.get_len(fileset.Fileset.IMG_TABLE) \
            + self.fileset.get_len(fileset.Fileset.DET_ANN_TABLE) \
            + self.fileset.get_len(fileset.Fileset.SEG_ANN_TABLE)
        table = Videoset.UPLOADTABLE
        if not self.fileset.has_table(table):
            return (len == 0)

        need_upload_cnt = len
        need_upload_cnt -= self.fileset.get_len(table)
        if need_upload_cnt > 0:
            return False

        return True

    def add_video(self, dir):
        if self.videoset and not self.videoset.find_video(dir):
            self.videos.append(dir)
            if len(self.videos) > Videoset.VIDEOMAXCNT:
                self.videoset.add_videos(self.videos)
                self.videos = []
            if not self.videoset_changed:
                self.add_file(self.videorelpath)
                self.videoset_changed = True

    def add_file(self, relpath, table):
        self.files[table].append(relpath)
        if len(self.files[table]) > Videoset.FILEMXCNT:
            self.fileset.add_files(self.files[table], table)
            self.files[table] = []

    def flush(self):
        for table, files in self.files.items():
            if len(files) > 0:
                self.fileset.add_files(files, table)
                self.files[table] = []
        if len(self.videos) > 0:
            self.videoset.add_videos(self.videos)
            self.videos = []
        self.fileset.flush()
        if self.videoset is not None:
            self.videoset.flush()


class VideosetTable():
    TABLE_NAME = "videoset"
    SCHEMA_SQL = "path PRIMARY KEY"
    INSERT_SQL = "?"

    def __init__(self, path) -> None:
        mode = "?mode=rwc"
        p = Path(path)
        p = p.resolve()
        self.path = p.as_uri()
        self.uri = self.path + mode
        self.conn = sqlite3.connect(self.uri, uri=True)
        self.cursor = self.conn.cursor()
        sql = "SELECT name FROM sqlite_master" \
            + " WHERE type='table' ORDER BY name;"
        tables = []
        for row in self.cursor.execute(sql):
            tables.append(row[0])
        if not (VideosetTable.TABLE_NAME in tables):
            table = VideosetTable.TABLE_NAME
            self.create_table(table)

    def __del__(self) -> None:
        self.cursor = None
        self.conn.close()

    def create_table(self, table=None):
        if not table:
            table = VideosetTable.TABLE_NAME
        try:
            sql = "CREATE TABLE " + \
                + table + " (" \
                + VideosetTable.SCHEMA_SQL + ");"
            self.cursor.execute(sql)
        except BaseException as e:
            print("[FileSet.create_table] exception: {}".format(e))
            raise e
        return True

    def get_len(self):
        table = VideosetTable.TABLE_NAME
        sql = "SELECT COUNT(*) FROM " + table + ";"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return int(r[0])

    def check_videos(self, checker):
        table = VideosetTable.TABLE_NAME
        sql = "SELECT * FROM " + table + ";"
        for r in self.cursor.execute(sql):
            checker(r[0])

    def add_videos(self, files):
        table = VideosetTable.TABLE_NAME
        sql = "INSERT INTO " + table \
            + " VALUES (" + VideosetTable.INSERT_SQL() + ");"
        self.cursor.executemany(sql, files)

    def find_video(self, video):
        table = VideosetTable.TABLE_NAME
        sql = "SELECT * FROM " + table \
            + " WHERE path=\"" + video \
            + "\";"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return r is not None

    def flush(self):
        self.conn.commit()


# VideoFilePath ：wrapper for video file name translation!
class VideoFilePath():
    @staticmethod
    def split_path(path):
        (head, tail) = os.path.split(path)
        names = [tail]
        while head:
            (head, tail) = os.path.split(path)
            names.append(tail)
        return names

    @staticmethod
    def merge_path(names):
        path = names[0]
        for i in range(1, len(names)):
            path = os.path.join(names[i], path)
        return path

    @staticmethod
    def split_fname_V1(name):
        names = name.rsplit('_')
        names.reverse()
        return names

    @staticmethod
    def split_fname_V2(name):
        names = name.rsplit('+')
        names.reverse()
        return names

    @staticmethod
    def split_fname(name):
        return VideoFilePath.split_fname_V2(name)

    @staticmethod
    def merge_fname_V1(names):
        name = names[0]
        for i in range(1, len(names)):
            name = names[i] + '_' + name
        return name

    @staticmethod
    def merge_fname_V2(names):
        name = names[0]
        for i in range(1, len(names)):
            name = names[i] + '+' + name
        return name

    @staticmethod
    def merge_fname(names):
        return VideoFilePath.merge_fname_V2(names)

    def __init__(self, input, isPath=True, nameV1=False) -> None:
        self.valid = False
        self.input = input
        self.isPath = isPath
        if isPath:
            #  /500000/20220323-002/04/data_video.h265
            names = VideoFilePath.split_path(input)
            self.names = names
            if names[0].contain('.'):
                self.hasVideo = True
                self.video = names[0]
                names = names[1:]
            else:
                self.hasVideo = False
                self.video = 'data_video.h265'
            self.hasFrame = False
            self.frame = None
            self.region = names[-1]
            self.datecar = names[-2]
            self.serial = names[:len(names) - 2]
        else:
            #  500000_20220608-004_02_02-1_38600.jpg
            if nameV1:
                names = VideoFilePath.split_fname_V1(input)
            else:
                names = VideoFilePath.split_fname(input)
            self.names = names
            self.hasFrame = True
            self.frame = names[0]
            self.hasVideo = False
            self.video = 'data_video.h265'
            names = names[1:]
            self.serial = names[:len(names) - 2]
            self.region = names[-1]
            self.datecar = names[-2]
        self.valid = (len(self.serial) > 0)
        self.fname_ = None
        return

    def __del__(self) -> None:
        pass

    def get_dir(self):
        names = self.serial.copy()
        names.append(self.datecar)
        names.append(self.region)
        return VideoFilePath.merge_path(names)

    def get_file(self):
        names = self.serial.copy()
        names.append(self.datecar)
        names.append(self.region)
        fname = VideoFilePath.merge_fname(names)
        self.fname_ = fname
        return fname

    def get_frame(self):
        if not self.hasFrame:
            return None

        if not self.fname_:
            self.get_file()

        names = [self.frame, self.fname_]
        return VideoFilePath.merge_fname(names)

    def set_frame(self, frameid):
        self.hasFrame = True
        self.frame = str(frameid) + ".jpg"


# EOF
