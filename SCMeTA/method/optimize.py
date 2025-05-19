import pandas as pd
import numpy as np
from typing import Callable


def optimize_sequence(
        mat: pd.DataFrame,
        func: Callable[[pd.DataFrame, float], list]
):
    """Optimize the sequence of the cell regions.

    Parameters
    ----------
    mat : pd.DataFrame
        The raw data.
    func : callable(mat: pd.DataFrame, max_ratio: float) -> list
        The function to find the cell or metabolite regions

    Returns
    -------
    optimized : tuple[float, list]
        The optimized value parameter, and the optimized value.
    """
    x_data = np.arange(0, 0.9, 0.01)
    cell_counts_list = [func(mat, i) for i in x_data]
    y_data = np.array([len(cell_counts) for cell_counts in cell_counts_list])
    inflection_point = find_inflection_point(x_data, y_data)
    return x_data[inflection_point], cell_counts_list[inflection_point]


# 二分法快速找到拐点的过程函数
def find_inflection_point(x_data, y_data):
    start_point = np.array([x_data[0], y_data[0]])
    end_point = np.array([x_data[-1], y_data[-1]])
    slope = (end_point[1] - start_point[1]) / (end_point[0] - start_point[0])

    def is_above_line(x, y, line_start_x, line_start_y, slope):
        # 给定点在直线的上方返回 True
        return y > slope * (x - line_start_x) + line_start_y

    left = 0
    right = len(x_data)

    while left < right:
        mid = (left + right) // 2
        line_start_x = x_data[mid]
        line_start_y = y_data[mid]

        # 检查相邻的点是否在直线上方
        if is_above_line(x_data[mid + 1], y_data[mid + 1], line_start_x, line_start_y, slope):
            right = mid
        else:
            left = mid + 1
    return left

