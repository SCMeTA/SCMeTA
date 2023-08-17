import pandas as pd
from itertools import chain


def collect_noise(mat: pd.DataFrame, cell_pos: list[list], self_sub: bool = False) -> list[pd.DataFrame]:
    noise_list = []
    for index, group in enumerate(cell_pos):
        noise_start = 1 if index == 0 else group[0] - 1
        noise_end = group[0] - 1
        noise_mean = mat.loc[noise_start:noise_end].mean()
        noise_list.append(noise_mean)
        if self_sub:
            mat.loc[noise_start:noise_end] = mat.loc[noise_start:noise_end] - noise_mean
    noise_list.append(mat.loc[cell_pos[-1][-1] + 1:].mean())
    return noise_list


def noise_subtract(
    mat: pd.DataFrame, cell_pos: list, method: str = "specific"
) -> pd.DataFrame:
    """Back subtract the noise from the raw data.
    Parameters
    ----------
    mat : pd.DataFrame
        The raw data.
    cell_pos : list
        The cell positions.
    method : str, optional
    Returns
    -------
    pd.DataFrame
        The back subtracted data.
    """
    noise_list = collect_noise(mat, cell_pos, self_sub=True)
    if method == "specific":
        for index, group in enumerate(cell_pos):
            noise_mean = pd.concat(
                [noise_list[index], noise_list[index + 1]], axis=1
            ).mean(axis=1)
            mat.loc[group] = mat.loc[group] - noise_mean
    elif method == "global":
        noise_list = list(chain.from_iterable(noise_list))
        noise_mean = mat.loc[noise_list].mean()
        for group in cell_pos:
            mat.loc[group] = mat.loc[group] - noise_mean
    mat = mat.clip(lower=0)
    return mat


def filter_assem(
    mat: pd.DataFrame,
    cell_mat: pd.DataFrame,
    cell_pos: list[list],
    snr: float = 3.0,
    method: str = "specific",
) -> pd.DataFrame:
    """Filter the assembly data.
    Parameters
    ----------
    mat : pd.DataFrame
        The raw data.
    cell_mat : pd.DataFrame
        The cell data.
    cell_pos : list[list]
        The cell positions.
    snr : float, optional
        The signal-to-noise ratio.
    method : str
        The filter method.
    Returns
    -------
    pd.DataFrame
        The filtered data.
    """
    noise_list = collect_noise(mat, cell_pos)
    mask = pd.DataFrame()
    if method == "specific":
        cell_list = cell_mat.index.tolist()
        for pos in cell_list:
            noise_filter = (
                pd.concat([noise_list[pos], noise_list[pos + 1]], axis=1).mean(axis=1)
                * snr
            )
            mask_item = cell_mat.loc[pos] > noise_filter
            mask = pd.concat([mask, mask_item], axis=1)
    elif method == "global":
        noise_list = list(chain.from_iterable(noise_list))
        noise_filter = mat.loc[noise_list].mean() * snr
        mask = pd.concat([mask, cell_mat > noise_filter], axis=1)
    mask = mask.T
    mask.index = cell_mat.index
    cell_mat = cell_mat[mask]
    # Remove the empty columns
    cell_mat = cell_mat.dropna(axis=1, how="all")
    return cell_mat
