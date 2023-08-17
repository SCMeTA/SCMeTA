import pandas as pd


def combine_mat(mat_list) -> pd.DataFrame:
    """
    Combine a list of matrices into a single matrix.
    """
    return pd.concat(mat_list).sort_index(axis=1)
