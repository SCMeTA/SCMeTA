import numpy as np
import pandas as pd

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
    temp = [sum_df(_raw.loc[scan:scan], scan) for scan in range(min_scan, max_scan + 1)]
    return pd.concat(temp)


def filter_occ(
    raw: pd.DataFrame, resolution: float = 0.01, count: int = 10
) -> pd.DataFrame:
    """
    Filter out peaks that occur less than count times in the data.
    :param raw: Raw data.
    :param resolution: Resolution of m/z.
    :param count: Minimum number of occurrences.
    :return: List of filtered peaks.
    """
    process = peaks_combine(raw, resolution)
    peaks = process["Mass"].value_counts()
    peaks = peaks[peaks >= count]
    process = process[process["Mass"].isin(peaks.index)]
    return process


def filter_mat(
    mat_list: list[pd.DataFrame], threshold: float = 0.2, lock: bool = False, method: str = "all"
) -> list[pd.DataFrame]:
    """Filter matrix by count
    Args:
        mat_list (list[pd.DataFrame]): List of matrix
        threshold (float, optional): Threshold. Defaults to 0.2.
        lock (bool, optional): Whether to lock the mz list. Defaults to False.
    Returns:
        pd.DataFrame: Filtered matrix
    """
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


if __name__ == '__main__':
    # func any threshold
    # func all threshold
    pass
