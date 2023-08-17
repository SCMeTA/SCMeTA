import pandas as pd
import numpy as np


def round_columns(mat: pd.DataFrame, resolution: float = 0.01, axis=1) -> pd.DataFrame:
    """Round the values of a column to n decimal places.

    Args:
        mat (pd.DataFrame): The matrix to round.
        resolution (float, optional): The resolution to round to. Defaults to 0.01.
        axis (int, optional): The axis to round. Defaults to 1.
    Returns:
        pd.DataFrame: The rounded matrix.
    """
    n = int(np.log10(1 / resolution))
    if axis == 1:
        c = mat.columns.to_numpy(dtype=float)
        c = np.round(c, n)
        mat.columns = c
    elif axis == 0:
        c = mat.index.to_numpy(dtype=float)
        c = np.round(c, n)
        mat.index = c
    return mat


def round_rows(
    mat: pd.DataFrame, key: str = "Mass", resolution: float = 0.01
) -> pd.DataFrame:
    """Round the values of a row to n decimal places.

    Args:
        mat (pd.DataFrame): The matrix to round.
        key (str): The key to round.
        resolution (float, optional): The resolution to round to. Defaults to 0.01.

    Returns:
        pd.DataFrame: The rounded matrix.
    """
    n = int(np.log10(1 / resolution))
    c = mat.loc[:, key].to_numpy(dtype=float)
    c = np.round(c, n)
    mat.loc[:, key] = c
    mat = mat.groupby(key).sum()
    return mat
