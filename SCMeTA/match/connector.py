import sqlite3

from SCMeTA.config import PARAMETERS


class Connector:
    def __init__(self):
        self.conn = sqlite3.connect(PARAMETERS.dbpath)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.conn = sqlite3.connect(PARAMETERS.dbpath)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def search(self, mz: float, rl: float = 1.008, tol: float = 0.01):
        mass = mz - rl
        self.cursor.execute(
            f"SELECT * FROM hmdb WHERE monisotopic_molecular_weight BETWEEN {mass - tol} AND {mass + tol}"
        )
        return self.cursor.fetchall()

    def search_list(self, mz_list: list[float], rl: float = 1.008, tol: float = 0.01) -> dict[float, list]:
        return {mz: self.search(mz, rl, tol) for mz in mz_list}


