import sqlite3
import os
import uuid
filepath = os.path.dirname(os.path.realpath(__file__))


class SQL:
    def __init__(self, db_path, table):
        self.db_path = db_path
        self.table = table
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

    def create_collumns(self, collumns):
        try:
            for x in collumns:
                self.c.execute(f"ALTER TABLE {self.table} ADD COLUMN {x}")
        except sqlite3.OperationalError as e:
            print(e)
            if e.args[0] == "no such table: " + self.table:
                self.c.execute(f"CREATE TABLE {self.table} ({', '.join(collumns)})")
                self.conn.commit()
            elif e.args[0] == "table " + self.table + " already exists":
                pass
            self.c.execute(f"CREATE TABLE {self.table} ({', '.join(collumns)})")
            self.conn.commit()
            print(f"Table {self.table} created")

        self.conn.commit()

    def getcollumn(self, collumn):
        self.c.execute("SELECT " + collumn + " FROM " + self.table)
        return self.c.fetchall()

    def get(self, collumn, value):
        self.c.execute(f"SELECT * FROM {self.table} WHERE {collumn}='{value}'")
        return self.c.fetchall()

    def add(self, collumns, values):
        self.c.execute(
            f"INSERT INTO {self.table} ({', '.join(collumns)}) VALUES ({', '.join(values)})")
        self.conn.commit()

    def set(self, collumn, vid, newval):
        self.c.execute(
            f"UPDATE {self.table} SET {collumn}=\"{newval}\" WHERE id='{vid}'")
        self.conn.commit()

    def find_unused_id(self):
        usedids = self.getcollumn("id")
        checkid = uuid.uuid4()
        checkid = str(checkid)
        checkid = checkid.replace("-", "")
        while checkid in usedids:
            checkid = uuid.uuid4()
            checkid = str(checkid)
            checkid = checkid.reaplce("-", "")
        return checkid


if __name__ == "__main__":
    sql = SQL(f"{filepath}/data.db", "files")
    sql.create_collumns(["watched"])
