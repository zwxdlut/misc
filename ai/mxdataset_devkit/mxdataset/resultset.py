import sqlite3
from pathlib import Path

from mxdataset.util import parser_config


# global dict
reader_resultsets = {}
writer_resultsets = {}


# global functions
def CreateResultset(path, writer=False, memory=False):
    if writer:
        if path in writer_resultsets:
            resultset = writer_resultsets[path]
        else:
            resultset = Resultset(path, writer, memory)
            writer_resultsets[resultset.path] = resultset
    else:
        if path in reader_resultsets:
            resultset = reader_resultsets[path]
        else:
            resultset = Resultset(path, writer, memory)
            reader_resultsets[resultset.path] = resultset

    resultset.users += 1
    return resultset


def ReleaseResultset(resultset):
    resultset.users -= 1
    if resultset.users == 1:
        if resultset.writer:
            del writer_resultsets[resultset.path]
        else:
            del reader_resultsets[resultset.path]
    return


def ann_generator(last_id, ann_records):
    for record in ann_records:
        if record.valid:
            last_id = last_id + 1
            record.set_id(last_id)
            row = record.make_insertion()
            yield row


# class
class Resultset():
    def __init__(self, path, writer, memory) -> None:
        self.annotations = {}
        self.views = {}
        self.categories = {}
        self.users = 1

        mode = "?mode=rwc" if writer else "?mode=ro"
        self.writer = writer
        self.memory = memory
        if not memory:
            p = Path(path)
            p = p.resolve()
            self.path = p.as_uri()
            self.uri = self.path + mode
        else:
            self.path = "memory:" + path
            mode = "?mode=memory&cache=shared"
            self.uri = "file:" + path + mode

        self.conn = sqlite3.connect(self.uri, uri=True)
        self.cursor = self.conn.cursor()
        sql = "SELECT name FROM sqlite_master" \
            + " WHERE type='table' ORDER BY name;"
        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            table = row[0]
            prefix = table[0:2]
            table = table[2:]
            if prefix == "A_":
                self.add_annotation(table)
            elif prefix == "V_":
                self.add_view(table)
            elif prefix == "C_":
                self.add_category(table)
            else:
                print("[Resultset.__init__] unknown table: " + row[0])

        if writer:
            cfg = parser_config()
            for cls, cats in cfg["categories"].items():
                self.create_category(cls)
                table = self.get_category(cls)
                table.clear_table()
                table.add_categories(cats)
                table.flush()

    def __del__(self) -> None:
        self.annotations.clear()
        self.categories.clear()
        self.views.clear()
        self.conn.close()
        self.conn = None

    def create_annotation(self, ann_cls):
        if not (ann_cls in self.annotations):
            cursor = self.conn.cursor()
            table = AnnotationTable(ann_cls, cursor)
            table.create_table()
            self.annotations[ann_cls] = table

    def add_annotation(self, ann_cls):
        if not (ann_cls in self.annotations):
            cursor = self.conn.cursor()
            table = AnnotationTable(ann_cls, cursor)
            self.annotations[ann_cls] = table
            table.check_valid()

    def get_annotation(self, ann_cls):
        return self.annotations[ann_cls]

    def list_annotations(self):
        return self.annotations.keys()

    def has_annotation(self, ann_cls):
        return ann_cls in self.annotations

    def create_view(self, view, fromTable, filterSQL):
        if not (view in self.views):
            cursor = self.conn.cursor()
            table = AnnotationTable(view, cursor, True)
            table.create_view(fromTable, filterSQL)
            self.views[view] = table

    def add_view(self, view):
        if not (view in self.views):
            cursor = self.conn.cursor()
            table = AnnotationTable(view, cursor)
            self.views[view] = table

    def get_view(self, view):
        return self.views[view]

    def list_views(self):
        return self.views.keys()

    def has_view(self, view):
        return view in self.views

    def drop_views(self):
        for view in self.views:
            view.drop_table()
        self.views.clear()
        self.flush()

    def get_table(self, table, isview):
        if isview:
            return self.get_view(table)
        else:
            return self.get_annotation(table)

    def create_category(self, cat_cls):
        if not (cat_cls in self.categories):
            cursor = self.conn.cursor()
            table = CategoryTable(cat_cls, cursor)
            table.create_table()
            self.categories[cat_cls] = table

    def add_category(self, cat_cls):
        if not (cat_cls in self.categories):
            cursor = self.conn.cursor()
            table = CategoryTable(cat_cls, cursor)
            self.categories[cat_cls] = table
            table.check_valid()

    def get_category(self, cat_cls):
        return self.categories[cat_cls]

    def flush(self):
        self.conn.commit()


class AnnotationTable():
    def __init__(self, table, cursor, isview=False) -> None:
        self.table = table
        self.tablename = ("V_" if isview else "A_") + table
        self.cursor = cursor
        self.isview = isview

    def __del__(self) -> None:
        cursor = self.cursor
        self.cursor = None
        del cursor

    def create_table(self):
        result = False
        try:
            sql = "CREATE TABLE " + self.tablename \
                + " (" + AnnotationRecord.SchemaSQL() + ");"
            self.cursor.execute(sql)
            # self.cursor.commit()
            result = True
        except BaseException as e:
            print("[AnnotationTable.create_table] exception: {}".format(e))
            raise e
        return result

    def drop_table(self):
        sql = "DROP TABLE " + self.tablename + ";"
        self.cursor.execute(sql)

    def create_view(self, fromTable, filterSQL):
        self.create_table()
        sql = "SELECT *create_table FROM A_" + fromTable \
            + " " + filterSQL + ";"
        records = []
        for row in self.cursor.execute(sql):
            r = AnnotationRecord(row)
            r.set_rid(r.id)
            records.append(r)
            if len(records) > 200:
                self.add_records(records)
                records = []
        self.add_records(records)
        self.flush()

    def check_valid(self):
        if self.get_len() != (self.get_lastid() + 1):
            err = "AnnotationTable " \
                + self.tablename \
                + " not valid!"
            raise Exception(err)
        return True

    def get_lastid(self):
        sql = "SELECT id FROM " + self.tablename \
            + " ORDER BY id DESC LIMIT 10;"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return int(r[0]) if r else -1

    def get_len(self):
        sql = "SELECT COUNT(*) FROM " \
            + self.tablename + ";"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return int(r[0])

    def get_record(self, id):
        sql = "SELECT * FROM " + self.tablename \
            + " WHERE id = " + str(id) + ";"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return AnnotationRecord(r) if r else None

    def __iter__(self):
        sql = "SELECT * FROM " + self.tablename + ";"
        self.cursor.execute(sql)
        return self

    def __next__(self):
        r = self.cursor.fetchone()
        if r is None:
            raise StopIteration
        return AnnotationRecord(r)

    def add_records(self, records):
        lastid = self.get_lastid()
        sql = "INSERT OR REPLACE INTO " + self.tablename \
            + " VALUES (" + AnnotationRecord.InsertSQL() + ");"
        self.cursor.executemany(sql, ann_generator(lastid, records))

    def flush(self):
        self.cursor.connection.commit()


class AnnotationRecord():
    FLAG_UNKNOWN = 0x00
    FLAG_IMAGESET = 0x01
    FLAG_VIDEOSET = 0x02

    @staticmethod
    def SchemaSQL():
        sql = "id INTEGER PRIMARY KEY ASC," \
            + "date,flag,rid," \
            + "ann_dir,ann_zip,ann_file," \
            + "img_dir,img_zip,img_file," \
            + "UNIQUE (ann_dir, ann_file) ON CONFLICT REPLACE"
        return sql

    @staticmethod
    def InsertSQL():
        return "?,?,?,?,?,?,?,?,?,?"

    def __init__(self, row=None) -> None:
        if row:
            self.id = row[0]
            self.date = row[1]
            self.flag = row[2]
            self.rid = row[3]
            self.ann_dir = row[4]
            self.ann_zip = row[5]
            self.ann_file = row[6]
            self.img_dir = row[7]
            self.img_zip = row[8]
            self.img_file = row[9]
            self.valid = True
        else:
            self.valid = False

    def __del__(self) -> None:
        pass

    def set_id(self, id):
        self.id = id
        self.rid = None

    def set_ann(self, ann_zip, ann_file, ann_dir=None):
        self.ann_dir = ann_dir
        self.ann_zip = ann_zip
        self.ann_file = ann_file

    def set_img(self, img_zip, img_file, img_dir=None):
        self.img_dir = img_dir
        self.img_zip = img_zip
        self.img_file = img_file

    def set_date(self, date):
        self.date = date

    def set_rid(self, rid):
        self.rid = rid

    def set_flag(self, flag):
        self.flag = flag

    def set_valid(self, valid=True):
        self.valid = valid

    def make_insertion(self):
        return (self.id, self.date, self.flag, self.rid,
                self.ann_dir, self.ann_zip, self.ann_file,
                self.img_dir, self.img_zip, self.img_file)


class CategoryTable():
    SCHEMA_SQL = "id INTEGER PRIMARY KEY ASC, " \
        "name TEXT, cvat_catid INTEGER"
    INSERT_SQL = "?,?"

    def __init__(self, table, cursor) -> None:
        self.table = table
        self.tablename = "C_" + table
        self.cursor = cursor

    def __del__(self) -> None:
        cursor = self.cursor
        self.cursor = None
        del cursor

    def create_table(self):
        result = False
        try:
            sql = "CREATE TABLE " + self.tablename \
                + " (" + CategoryTable.SCHEMA_SQL + ");"
            self.cursor.execute(sql)
            # self.cursor.commit()
            result = True
        except BaseException as e:
            print("CategoryTable[create_table] exception: {}".format(e))
            raise e
        return result

    def clear_table(self):
        sql = "DELETE FROM " + self.tablename + ";"
        self.cursor.execute(sql)

    def drop_table(self):
        sql = "DROP TABLE " + self.tablename + ";"
        self.cursor.execute(sql)

    def check_valid(self):
        if self.get_len() != (self.get_lastid() + 1):
            err = "CategoryTable " \
                + self.tablename \
                + " not valid!"
            raise Exception(err)
        return True

    def get_lastid(self):
        sql = "SELECT id FROM " + self.tablename \
            + " ORDER BY id DESC LIMIT 10;"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return int(r[0]) if r else -1

    def get_len(self):
        sql = "SELECT COUNT(*) FROM " \
            + self.tablename + ";"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return int(r[0])

    def get_categories(self):
        sql = "SELECT * FROM " + self.tablename + ";"
        self.cursor.execute(sql)
        r = self.cursor.fetchall()
        return r

    def __iter__(self):
        sql = "SELECT * FROM " + self.tablename + ";"
        self.cursor.execute(sql)
        return self

    def __next__(self):
        r = self.cursor.fetchone()
        if r is None:
            raise StopIteration
        return r

    def add_categories(self, cats):
        lastid = self.get_lastid()
        sql = "INSERT OR REPLACE INTO " + self.tablename \
            + "(id, name) VALUES (" + CategoryTable.INSERT_SQL + ");"
        self.cursor.executemany(
            sql, [(lastid + i + 1, cat) for i, cat in enumerate(cats)])

    def flush(self):
        self.cursor.connection.commit()


# EOF
