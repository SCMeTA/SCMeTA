from matplotlib.figure import Axes
import pandas as pd

COLOR_KEY = [
    "firebrick",
    "darkorange",
    "gold",
    "greenyellow",
    "deepskyblue",
    "navy",
    "violet",
    "magenta",
    "pink",
    "black",
]


def box(data: dict[str, pd.DataFrame], h_statistic: float, p_value: float, ax: Axes):
    # 绘制箱线图
    values = [df.iloc[:, 0].T.to_numpy() for df in data.values()]
    labels = [name for name in data.keys()]
    ax.boxplot(values, labels=labels, showmeans=True, meanline=True, patch_artist=True)

    # 设定颜色
    for patch, color in zip(ax.artists, COLOR_KEY):
        patch.set_facecolor(color)

    # 设置图表标题和坐标轴标签
    ax.set_title(f"Kruskal-Wallis H Test Result")
    ax.set_xlabel('Data Group')
    ax.set_ylabel('Value')
