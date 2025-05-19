import numpy as np
import pandas as pd
from .optimize import optimize_sequence

from SCMeTA.config import INCLUDE_LIST, EXCLUDE_LIST


def sum_df(df, scan) -> pd.DataFrame:
    df = df.groupby("Mass").sum().reset_index()
    df.insert(0, "Scan", scan)
    df = df.set_index("Scan")
    return df


def peaks_combine(_raw: pd.DataFrame, resolution: float = 0.01) -> pd.DataFrame:
    try:
        _raw["Mass"] = _raw["Mass"].divide(0.01).apply(np.floor).mul(0.01)
    except AttributeError:
        _raw["Mass"] = np.floor(_raw["Mass"] / resolution) * resolution
    max_scan = _raw.index.max()
    min_scan = _raw.index.min()
    temp = [sum_df(_raw.loc[scan], scan) for scan in range(min_scan, max_scan + 1)]
    return pd.concat(temp)

def calculate_ppm(mz1: float, mz2: float) -> float:
    """
    Calculate the ppm (parts per million) between two m/z values.
    :param mz1: The first m/z value.
    :param mz2: The second m/z value.
    :return: The ppm value.
    """
    return abs((mz1 - mz2) / mz1) * 1e6

def calculate_mz_range(mz: float, tolerance: int = 5) -> tuple:
    """
    Calculate the m/z range for a given m/z value and tolerance.
    :param mz: The m/z value.
    :param tolerance: The tolerance for m/z, default is 5 ppm.
    :return: A tuple containing the lower and upper bounds of the m/z range.
    """
    lower_bound = mz - (mz * tolerance / 1e6)
    upper_bound = mz + (mz * tolerance / 1e6)
    return lower_bound, upper_bound

def get_mz_list(total_index: list, tolerance: int = 5) -> list:
    """
    Get the m/z list from the total index.
    :param total_index: The index of the dataframe.
    :param tolerance: The tolerance for m/z, default is 5 ppm.
    :return: The m/z list.
    """
    # sort the index and remove duplicates
    total_index = sorted(set(total_index))
    # calculate the ppm for each m/z value
    # ppm_list = [calculate_ppm(total_index[i], total_index[i + 1]) for i in range(len(total_index) - 1)]
    mz_list_start = [total_index[i] for i in range(len(total_index) - 1) if calculate_ppm(total_index[i], total_index[i + 1]) > tolerance]
    mz_list_end = [total_index[i] for i in range(len(total_index) - 1) if calculate_ppm(total_index[-i + 1], total_index[- i]) > tolerance]
    # reverse the end list
    mz_list_end = mz_list_end[::-1]

    # for i in range(len(total_index) - 1):
    #     if calculate_ppm(total_index[i], total_index[i + 1]) < tolerance:
    #         mz_list_from_start.append(total_index[i])
    #     if calculate_ppm(total_index[-i + 1], total_index[- i]) > tolerance:
    #         mz_list_from_end.append(total_index[i])
    mz_list = [(start, end) for start, end in zip(mz_list_start, mz_list_end)]
    return mz_list


def combine_peaks(cell_mat: pd.DataFrame, interval: float = 0.01) -> pd.DataFrame:
    cell_mat = cell_mat.sort_index(axis=1)
    diff = cell_mat.columns.to_series().diff(periods=-1).round(2)
    diff[diff != -interval] = 0
    cell_mat.columns = cell_mat.columns - diff
    cell_mat.columns = cell_mat.columns.to_series().round(2)
    cell_mat = cell_mat.T.groupby(cell_mat.columns).sum()
    cell_mat = cell_mat.replace(0, np.nan)
    return cell_mat.T


def filter_occ(
        raw: pd.DataFrame,
        resolution: float = 0.01,
        tolerance: int = 5,
        count: int = 10
) -> pd.DataFrame:
    """
    Filter out peaks that occur less than count times in the data.
    :param raw: Raw data.
    :param resolution: Resolution of m/z.
    :param tolerance: Tolerance for m/z, default is 5 ppm.
    :param count: Minimum number of occurrences.
    :return: List of filtered peaks.
    """
    process = peaks_combine(raw, resolution)
    peaks = process["Mass"].value_counts()
    peaks = peaks[peaks >= count]
    process = process[process["Mass"].isin(peaks.index)]
    return process


def lock_mz(mat: pd.DataFrame) -> pd.DataFrame:
    """Lock mz list
    Args:
        mat: cell matrix.
    Returns:
        pd.DataFrame: Locked matrix
    """
    include_bool = mat.columns.isin(INCLUDE_LIST)
    exclude_bool = mat.columns.isin(EXCLUDE_LIST)
    mat = mat.loc[:, ~exclude_bool]
    mat = mat.loc[:, include_bool | ~include_bool]
    return mat


def filter_mat(
    mat_list: list[pd.DataFrame], threshold: float | str = 0.2, lock: bool = False, method: str = "all"
) -> list[pd.DataFrame] | None:
    """Filter matrix by count
    Args:
        mat_list (list[pd.DataFrame]): List of a matrix
        threshold (float, optional): Threshold. Defaults to 0.2, if "auto", it will auto optimize the threshold.
        lock (bool, optional): Whether to lock the mz list. Defaults to False.
        method (str, optional): Method to filter. Defaults to "all". Available values are "all" and "any".
    Returns:
        pd.DataFrame: Filtered matrix
    """
    if threshold == "auto":
        return None
    else:
        if method == "all":
            count = sum([mat.shape[0] for mat in mat_list]) * threshold
            large_mat = pd.concat(mat_list)
            large_mat.sort_index(axis=1, inplace=True)
            mz_bool = large_mat.count() >= count
            if lock:
                include_bool = large_mat.columns.isin(INCLUDE_LIST)
                exclude_bool = large_mat.columns.isin(EXCLUDE_LIST)
                mz_bool = mz_bool | include_bool
                mz_bool = mz_bool & ~exclude_bool
            mz_list = mz_bool[mz_bool].index
            # if mat in mat_list doesn't have the mz, it will be filled with NaN
            mat_list = [mat.reindex(columns=mz_list, fill_value=None) for mat in mat_list]
            mat_list = [mat[mz_list] for mat in mat_list]
            return mat_list
        elif method == "any":
            index_lists = []
            for mat in mat_list:
                count = mat.shape[0] * threshold
                mz_bool = mat.count() >= count
                if lock:
                    include_bool = mz_bool.index.isin(INCLUDE_LIST)
                    exclude_bool = mz_bool.index.isin(EXCLUDE_LIST)
                    mz_bool = mz_bool | include_bool
                    mz_bool = mz_bool & ~exclude_bool
                index_lists.append(mz_bool[mz_bool])
            mz_bool = pd.concat(index_lists, axis=1)
            mz_list = mz_bool.index
            new_mat_list = []
            for mat in mat_list:
                mat = mat.reindex(columns=mz_list, fill_value=None)
                mat = mat[mz_list]
                new_mat_list.append(mat)
            return new_mat_list
        return None