import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import ttest_ind, f_oneway


def euclidean_distance(data_list1: np.ndarray, data_list2: np.ndarray):
    euclidean_dist = cdist(data_list1, data_list2, 'euclidean')
    return euclidean_dist


# 计算两组数据间的曼哈顿距离
def manhattan_distance(data_list1: np.ndarray, data_list2: np.ndarray):
    manhattan_dist = cdist(data_list1, data_list2, 'cityblock')
    return manhattan_dist


def t_test(data1: np.ndarray, data2: np.ndarray):
    t, p = ttest_ind(data1, data2)
    return t, p


def anova_test(data_list: list[np.ndarray]):
    f, p = f_oneway(*data_list)
    return f, p
# t-检验比较两组数据是否有显著差异


if __name__ == '__main__':
    pass