import numpy as np
import pandas as pd

from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.ticker as ticker

from SCMeTA.method import combine_mat

CMAP_KEY = {
    "jet": plt.cm.jet,
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
    color_map="jet",
    func: str = "NO_LOG",
    title: str = "Heatmap",
):
    mat = combine_mat(mat_list.values()).fillna(0.000001)
    mat = mat.apply(LOG_KEY[func])
    # normalize the matrix from 0 to 1
    mat = (mat - mat.min().min()) / (mat.max().max() - mat.min().min())
    mat = mat.T
    fig.subplots_adjust(right=1, left=0.15, top=0.9, bottom=0.1)
    im = ax.imshow(
        mat, cmap=CMAP_KEY[color_map], aspect="auto"
    )
    fig.colorbar(im, ax=ax)

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

    # draw lines between each group of cells
    for i in range(len(new_cell_numb) - 1):
        ax.axvline(x=new_cell_numb[i] + 0.5, color='black', linestyle='--', linewidth=0.5)

    ax.set_xlabel("Cell")  # 设置x轴标题
    ax.set_ylabel("Mass")  # 设置y轴标题
    ax.set_title(title)  # 设置图像标题

    ax.xaxis.set_major_locator(ticker.FixedLocator(new_cell_numb))  # 设置x轴坐标的定位
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(cell_name))  # 设置x轴坐标的名称
    ax.set_yticks(np.arange(len(mass)), labels=mass)  # 设置y轴坐标的定位和名称
    # show total 30 y-axis ticks
    ax.yaxis.set_major_locator(ticker.MaxNLocator(20))
