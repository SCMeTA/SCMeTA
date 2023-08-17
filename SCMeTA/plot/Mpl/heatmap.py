import numpy as np
import pandas as pd

from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt
from matplotlib.figure import Figure, Axes
import matplotlib.ticker as ticker

from SCMeTA.method import combine_mat

CMAP_KEY = {
    "viridis": plt.cm.viridis,
    "plasma": plt.cm.plasma,
    "inferno": plt.cm.inferno,
    "magma": plt.cm.magma,
}

LOG_KEY = {
    "LOG10": np.log10,
    "LOG2": np.log2,
    "LOG": np.log,
    "NO_LOG": lambda x: x,
}


def heatmap(
    mat_list: dict[str, pd.DataFrame],
    cell_range: dict[str, int],
    ax: Axes,
    fig: Figure,
    color_map="viridis",
    func: str = "NO_LOG",
    title: str = "Heatmap",
):
    mat = combine_mat(mat_list.values()).fillna(0.00001)
    mat = mat.apply(LOG_KEY[func])
    mat = mat.T
    ax.imshow(
        mat, cmap=CMAP_KEY[color_map], aspect="auto"
    )  # aspect="auto"自动调整像素点，而非默认的正方形
    mass = mat.index.values

    cell_numb = list(cell_range.values())
    cell_name = list(cell_range.keys())

    # 横坐标以细胞名称命名
    new_cell_numb = [0] * len(cell_numb)
    for a in range(len(cell_numb)):
        if a == 0:
            new_cell_numb[a] = 0
        else:
            new_cell_numb[a] = new_cell_numb[a - 1] + cell_numb[a - 1]
    for b in range(len(cell_numb)):
        new_cell_numb[b] = new_cell_numb[b] + int(cell_numb[b] / 2)

    ax.set_xlabel("Cell")  # 设置x轴标题
    ax.set_ylabel("Mass")  # 设置y轴标题
    ax.set_title(title)  # 设置图像标题
    fig.colorbar(ScalarMappable(cmap=color_map))  # 使用color bar

    ax.xaxis.set_major_locator(ticker.FixedLocator(new_cell_numb))  # 设置x轴坐标的定位
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(cell_name))  # 设置x轴坐标的名称
    ax.set_yticks(np.arange(len(mass)), labels=mass)  # 设置y轴坐标的定位和名称
    ax.yaxis.set_major_locator(ticker.MultipleLocator(30))  # 每20个y坐标显示一次
