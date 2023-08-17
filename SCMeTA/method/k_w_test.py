import pandas as pd

from scipy.stats import kruskal


def k_w_test(data: dict[str, pd.DataFrame]):
    np_arrays = [df.iloc[:, 0].T.to_numpy() for df in data.values()]
    h_statistic, p_value = kruskal(*np_arrays)
    return h_statistic, p_value
