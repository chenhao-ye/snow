"""
Maintain durable data on the local machine with a key-value interface.
"""
import sqlite3
import re


class DurableMap:
    re_tname = re.compile(r"\A[a-zA-Z_][a-zA-Z0-9_]*\Z")

    def __init__(self, path: str, tname: str) -> None:
        # tname must be SQL-safe!
        assert self.re_tname.fullmatch(tname) is not None
        self.tname = tname
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()
        self.cur.execute(
            "SELECT count(name) "
            "FROM sqlite_schema "
            "WHERE type = 'table' AND name = :tname", {"tname": tname})

        if self.cur.fetchone()[0] == 0:
            self.cur.execute(
                f"CREATE TABLE {tname} (dm_key TEXT NOT NULL UNIQUE PRIMARY KEY, dm_val TEXT)"
            )
        self.con.commit()

    def close(self) -> None:
        self.con.close()

    def commit(self) -> None:
        self.con.commit()

    def get(self, key: str) -> str:
        res = self.cur.execute(
            f"SELECT dm_val FROM {self.tname} WHERE dm_key = :key", {
                "key": key
            }).fetchall()
        assert len(res) <= 1
        if len(res) == 1:
            return res[0][0]
        return None

    def put(self, key: str, val: str = None, commit: bool = True) -> None:
        self.cur.execute(
            f"INSERT OR REPLACE INTO {self.tname} (dm_key, dm_val) VALUES (:key, :val)",
            {
                "key": key,
                "val": val
            })
        if commit:
            self.commit()

    def insert(self, key: str, val: str = None, commit: bool = True) -> None:
        self.cur.execute(
            f"INSERT INTO {self.tname} (dm_key, dm_val) VALUES (:key, :val)", {
                "key": key,
                "val": val
            })
        if commit:
            self.commit()

    def update(self, key: str, val: str, commit: bool = True) -> None:
        self.cur.execute(
            f"UPDATE {self.tname} SET dm_val = :key WHERE dm_key = :val", {
                "key": key,
                "val": val
            })
        if commit:
            self.commit()

    def delete(self, key: str, commit: bool = True):
        self.cur.execute(f"DELETE FROM {self.tname} WHERE dm_key = :key",
                         {"key": key})
        if commit:
            self.commit()
