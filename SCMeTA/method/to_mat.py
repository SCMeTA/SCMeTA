import pandas as pd


def to_mat(data: pd.DataFrame) -> pd.DataFrame:
    mat = data.pivot_table(
        index="Scan",
        columns="Mass",
        values="Intensity",
    ).fillna(0)
    return mat


def to_list(mat: pd.DataFrame, cell_pos: list[list]) -> pd.DataFrame:
    index_list = mat.index
    index = [cell_pos[i][0] for i in index_list]
    mat.index = index
    mat = mat.stack().reset_index()
    mat.columns = ["Scan", "Mass", "Intensity"]
    mat.set_index("Scan", inplace=True)
    return mat
