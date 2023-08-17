import pandas as pd

from SCMeTA.match import Connector


class SearchDatabase:
    def __init__(self):
        pass

    @staticmethod
    def search_full(cell_mat: pd.DataFrame, **kwargs):
        mz_list = cell_mat.columns.to_list()
        with Connector() as conn:
            return conn.search_list(mz_list, **kwargs)

    def search_id(self, cell_mat: pd.DataFrame, **kwargs) -> dict[float, list[str]]:
        full_info = self.search_full(cell_mat, **kwargs)
        id = {}
        for mz, info in full_info.items():
            id[mz] = [i[1] for i in info]
        return id

    def search_name(self, cell_mat: pd.DataFrame, **kwargs) -> dict[float, list[str]]:
        full_info = self.search_full(cell_mat, **kwargs)
        name = {}
        for mz, info in full_info.items():
            name[mz] = [i[2] for i in info]
        return name
