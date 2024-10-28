import sqlite3
from pathlib import Path


def file_generator(lastid, files):
    for file in files:
        lastid = lastid + 1
        yield [lastid, file]


class Fileset():
    # file tables
    IMG_TABLE = "images"
    DET_ANN_TABLE = "detection_anns"
    SEG_ANN_TABLE = "segmentation_anns"
    FILE_TABLES = [IMG_TABLE, DET_ANN_TABLE, SEG_ANN_TABLE]
    FILE_SCHEMA_SQL = "id INTEGER PRIMARY KEY ASC, path UNIQUE"
    FILE_INSERT_SQL = "?,?"

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

        tables = {}
        self.tables = {}

        # check tables
        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            table = row[0]
            tables[table] = self.get_lastid(table)

        # initialize file tables
        for table in Fileset.FILE_TABLES:
            if not (table in tables):
                self.create_table(table)
                tables[table] = self.get_lastid(table)

        self.tables = tables

    def __del__(self) -> None:
        self.cursor = None
        self.conn.close()

    def has_table(self, table):
        return table in self.tables

    def create_table(self, table, schema=None):
        try:
            sql = "CREATE TABLE " \
                + table + " (" \
                + (Fileset.FILE_SCHEMA_SQL if not schema else schema) + ");"
            self.cursor.execute(sql)
        except BaseException as e:
            print("[FileSet.create_table] exception: {}".format(e))
            raise e
        self.tables[table] = self.get_lastid(table)
        return True

    def get_lastid(self, table):
        sql = "SELECT id FROM " + table \
            + " ORDER BY id DESC LIMIT 10;"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return int(r[0]) if r else -1

    def get_len(self, table):
        sql = "SELECT COUNT(*) FROM " \
            + table + ";"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return int(r[0])

    def check_table(self, checker, table):
        sql = "SELECT * FROM " + table + ";"
        for r in self.cursor.execute(sql):
            checker(r[0])

    def add_files(self, files, table):
        sql = "INSERT OR IGNORE INTO " + table \
            + " VALUES (" + Fileset.FILE_INSERT_SQL + ");"
        lastid = self.tables[table]
        self.tables[table] += len(files)
        self.cursor.executemany(sql, file_generator(lastid, files))

    def flush(self):
        self.conn.commit()

    def table_equal(self, table1, table2):
        sql = "SELECT id, path" \
            + " FROM " + table1 + " A" \
            + " WHERE NOT EXISTS" \
            + " (SELECT 1 FROM " + table2 + " B" \
            + "  WHERE A.id = B.id" \
            + "  and A.path = B.path" \
            + " );"
        self.cursor.execute(sql)
        r = self.cursor.fetchone()
        return r is None


# EOF
