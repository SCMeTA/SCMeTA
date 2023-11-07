from dataclasses import dataclass, field

import pandas as pd


@dataclass
class SCData:
    name: str
    raw: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    offset: float = 0
    process: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    mat: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    cell_pos: list = list[list[int]]
    cell_mat: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    cell_count = property(lambda self: self.cell_mat.shape[0])
    database: bool = False

    def clear(self):
        self.mat = pd.DataFrame()

    def set_offset(self, offset: float | None):
        if self.offset is None or self.offset == 0:
            self.offset = offset
            self.raw["Mass"] += offset
        elif offset is None or offset == 0:
            pass
        else:
            _offset = offset - self.offset
            self.offset = offset
            self.raw["Mass"] += _offset

    def cut(self, start: float | None, end: float | None):
        self.raw = self.raw.loc[start:end]

    def xic(self, mz: float):
        return self.process.loc[self.process["Mass"] == mz]

    def show(self, _type="xic", **kwargs):
        pass

    def get_scan(self, scan: int, data_type: str = "raw"):
        if data_type == "raw":
            return self.raw.loc[scan]
        elif data_type == "process":
            return self.process.loc[scan]
        elif data_type == "mat":
            return self.mat.loc[scan]
        elif data_type == "cell_mat":
            for index, sublist in enumerate(self.cell_pos):
                if scan in sublist:
                    return self.cell_mat.loc[index]
        else:
            raise ValueError("data_type must be 'raw', 'process', 'mat' or 'cell_mat'")

    def reset(self):
        self.process = pd.DataFrame()
        self.mat = pd.DataFrame()
        self.cell_pos = []
        self.cell_mat = pd.DataFrame()
        self.raw["Mass"] -= self.offset
        self.offset = 0.0
