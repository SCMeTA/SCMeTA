import pandas as pd
import numpy as np
from scipy.stats import zscore


def max_normalize(mat: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Normalize data by max method.
    Args:
        mat: A dataframe.

    Returns:
        A normalized dataframe.

    """
    cell_max = mat.max(axis=1)
    return mat.div(cell_max, axis=0)


def mz_normalize(mat: pd.DataFrame, mz: float = 760.58, **kwargs) -> pd.DataFrame:
    """
    Normalize data by mz method.
    Args:
        mat: A dataframe.
        mz: The mz value to normalize.

    Returns:
        A normalized dataframe.

    """
    mz_df = mat.loc[:, mz]
    return mat.div(mz_df, axis=0)


def zscore_normalize(mat: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Normalize data by zscore method.
    Args:
        mat: A dataframe.

    Returns:
        A normalized dataframe.

    """
    return mat.apply(zscore)


def sum_normalize(mat: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Normalize data by sum method.
    Args:
        mat: A dataframe.

    Returns:
        A normalized dataframe.

    """
    cell_sum = mat.sum(axis=1)
    return mat.div(cell_sum, axis=0)


def quantile_normalize(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Perform Quantile-normalization on the given DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame with cells as rows and m/z values as columns

    Returns:
        pd.DataFrame: Quantile-normalized DataFrame
    """
    normalized_df = df.copy()
    normalized_df.fillna(0, inplace=True)

    for col in normalized_df.columns:
        sorted_col = normalized_df[col].sort_values(ascending=True)
        mean_rank = sorted_col.mean()
        sorted_index = sorted_col.index
        sorted_col_normalized = sorted_col.rank(method="average")

        col_normalized = pd.Series(index=sorted_index, data=sorted_col_normalized * mean_rank)
        col_normalized.sort_index(inplace=True)

        normalized_df[col] = col_normalized

    return normalized_df


def filter_mat(mat: pd.DataFrame, **kwargs) -> pd.DataFrame:
    # Drop all NaN rows
    mat = mat.dropna(how="all")
    return mat


def log_normalize(df: pd.DataFrame, base: float = 2, **kwargs) -> pd.DataFrame:
    """Perform log normalization on the given DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame with cells as rows and m/z values as columns
        base (float): Base of the logarithm (default is 2)

    Returns:
        pd.DataFrame: Log-normalized DataFrame
    """
    normalized_df = df.copy()
    normalized_df = normalized_df.applymap(lambda x: np.log(x + 1, dtype='float64') / np.log(base, dtype='float64') if x > 0 else 0)
    return normalized_df


FUNCTION_KEY = {
    "zscore": zscore_normalize,
    "max": max_normalize,
    "mz": mz_normalize,
    "sum": sum_normalize,
    "quantile": quantile_normalize,
    "log": log_normalize,
}


def normalize(data: pd.DataFrame, method: list[str], **kwargs) -> pd.DataFrame:
    """
    Normalize data by different methods.
    Args:
        data: A dataframe.
        method: The method to normalize data.
        **kwargs: The parameters of the method.

    Returns:
        A normalized dataframe.

    """
    for m in method:
        try:
            data = FUNCTION_KEY[m](data, **kwargs)
        except KeyError:
            raise KeyError(f"Method {m} is not supported.")
    return data


