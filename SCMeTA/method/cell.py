import pandas as pd
from .optimize import optimize_sequence


def find_cell_index(xic: pd.DataFrame, max_ratio=0.1) -> list:
    max_intensity = xic.max()
    cell_region = xic[xic > max_ratio * max_intensity].index
    return cell_region.to_list()


def find_adjacent(cell_array: list) -> list[list]:
    cell_group = []
    for i in cell_array:
        if not cell_group or i != cell_group[-1][-1] + 1:
            cell_group.append([i])
        else:
            cell_group[-1].append(i)
    return cell_group


def find_cell(
    mat: pd.DataFrame, refer_mz: float = 760.58, max_ratio: float | str = 0.1
) -> list[list]:
    """Find the cell regions.

    Parameters
    ----------
    mat : pd.DataFrame
        The raw data.
    refer_mz : float, optional
        The reference m/z, by default 760.58
    max_ratio : float, optional
        The maximum ratio, by default 0.1, if value is "auto", it will auto optimize the max_ratio.

    Returns
    -------
    list[list]
        The cell regions.
    """
    xic = mat.loc[:, refer_mz].fillna(0)
    if max_ratio == "auto":
        best_ratio, cell_array = optimize_sequence(xic, find_cell_index)
    elif isinstance(max_ratio, float):
        cell_array = find_cell_index(xic, max_ratio=max_ratio)
    else:
        raise ValueError("max_ratio should be float or auto")
    return find_adjacent(cell_array)


def merge_cell(
    mat: pd.DataFrame, cell_pos: list[list], adjacent: int = 3
) -> pd.DataFrame:
    """Combine the cell regions.

    Parameters
    ----------
    mat : pd.DataFrame
        The raw data.
    cell_pos : list[list]
        The cell regions.
    adjacent : int, optional
        The adjacent cell regions, by default 3

    Returns
    -------
    pd.DataFrame
        The combined cell regions.
    """
    cell_series_list = []
    index_list = []
    for index, group in enumerate(cell_pos):
        if len(group) <= adjacent:
            cell_series_list.append(mat.loc[group].sum())
            index_list.append(index)
    cell_mat = pd.concat(cell_series_list, axis=1).T
    # Set index
    cell_mat.index = index_list
    cell_mat.index.name = "Scan"
    return cell_mat
