import pandas as pd
import numpy as np
from scipy import stats
from matplotlib.figure import Axes


def clean_df(
    df0: pd.DataFrame, df1: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, list]:
    df0.dropna(how="all", inplace=True, axis=1)
    df1.dropna(how="all", inplace=True, axis=1)
    col_0 = df0.columns.tolist()
    col_1 = df1.columns.tolist()
    columns = [c for c in col_0 if c in col_1]
    df0 = df0.loc[:, columns].fillna(0)
    df1 = df1.loc[:, columns].fillna(0)
    return df0, df1, columns


def volcano(
    mat1: pd.DataFrame,
    mat2: pd.DataFrame,
    name1: str,
    name2: str,
    ax: Axes,
    x_threshold: float = 1.0,
    y_threshold: float = 1.30103,
):
    df0, df1, columns = clean_df(mat1, mat2)

    _list1 = []
    _list0 = np.log2((df0.mean(axis=0) / df1.mean(axis=0)).tolist())
    for i in columns:  # 算差异的显著性
        _, p = stats.ttest_ind(df0.loc[:, i], df1.loc[:, i])
        # 做t-test，我省略了方差齐性检验
        _list1.append(-np.log(p))
        # 得到y轴数据的list

    df_volcano = pd.DataFrame({"Mass": columns, "x": _list0, "y": _list1})
    # 构造用于做火山图的dataframe

    # 分组染色
    df_volcano["group"] = "black"  # 增加一列，索引为group
    df_volcano.loc[
        (df_volcano.x > x_threshold) & (df_volcano.y > y_threshold), "group"
    ] = "tab:red"  # 右上角为红色
    df_volcano.loc[
        (df_volcano.x < -x_threshold) & (df_volcano.y > y_threshold), "group"
    ] = "tab:blue"  # 左上角为蓝色
    df_volcano.loc[df_volcano.y < y_threshold, "group"] = "dimgrey"  # 阈值以下点为灰色

    # 设置坐标轴范围
    x_min, x_max = -2, 2
    y_min, y_max = 0, 20

    # 绘制散点图
    ax.set(xlim=(x_min, x_max), ylim=(y_min, y_max), title="")  # 设置坐标轴的长度
    ax.scatter(df_volcano["x"], df_volcano["y"], s=2, c=df_volcano["group"])  # 设置标记大小
    ax.set_xlabel("log2(fold change)")
    ax.set_ylabel("-log10(P)")
    ax.spines["right"].set_visible(False)  # 去掉右边框
    ax.spines["top"].set_visible(False)  # 去掉上边框

    # 水平和竖直线
    ax.vlines(
        -x_threshold, y_min, y_max, color="dimgrey", linestyle="dashed", linewidth=1
    )  # 画竖直线
    ax.vlines(
        x_threshold, y_min, y_max, color="dimgrey", linestyle="dashed", linewidth=1
    )  # 画竖直线
    ax.hlines(
        y_threshold, x_min, x_max, color="dimgrey", linestyle="dashed", linewidth=1
    )  # 画竖水平线

    ax.set_xticks(range(-2, 3, 1))  # 设置x轴刻度起点和步长
    ax.set_yticks(range(0, 21, 5))  # 设置y轴刻度起点和步长

    # 把红点和蓝点标上Mass
    index0 = df_volcano[df_volcano.group == "tab:red"].index.tolist()
    index1 = df_volcano[df_volcano.group == "tab:blue"].index.tolist()
    for i in index0:
        ax.annotate(
            columns[i],
            xy=(_list0[i], _list1[i]),
            xytext=(_list0[i] + 0.02, _list1[i] + 0.02),
            size=2,
        )
        # 调整字号和位置
    for i in index1:
        ax.annotate(
            columns[i],
            xy=(_list0[i], _list1[i]),
            xytext=(_list0[i] + 0.02, _list1[i] + 0.02),
            size=2,
        )

    title = f"{name1} and {name2}"
    ax.set_title(title)
