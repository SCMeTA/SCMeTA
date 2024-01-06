from SCMeTA.method import to_mat, filter_occ
import pandas as pd


def lc_mean(lc_data, resolution=0.01, count=3, method='mean'):
    lc_data = filter_occ(lc_data, resolution=resolution, count=count)
    lc_data = to_mat(lc_data)
    if method == 'mean':
        return lc_data.mean(axis=0)
    elif method == 'max':
        return lc_data.max(axis=0)


def compare_lc(lc1: pd.DataFrame, lc2: pd.DataFrame, threshold=10):
    compare = lc2 - lc1
    compare = compare[compare > threshold]
    return compare


def noise_ratio(lc: pd.DataFrame, noise: pd.DataFrame, ratio=3):
    noise = noise * ratio
    compare = lc - noise
    compare = compare[compare > 0]
    return compare
