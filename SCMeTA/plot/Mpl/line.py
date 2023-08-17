import numpy as np
import pandas as pd
from matplotlib.figure import Axes


def line_df(data: pd.DataFrame, ax: Axes):
    x, y1, y2 = data.index, data.iloc[:, 0], data.iloc[:, 1]
    x_label, y_label = data.index.name, "Intensity"
    ax[0].plot(x, y1, color="black", linewidth=0.8)
    ax[1].plot(x, y2, color="red", linewidth=0.8)
    ax[0].set_title(data.columns[0])
    ax[1].set_title(data.columns[1])
    return x_label, y_label


def line(data: pd.DataFrame | np.ndarray, ax: Axes | np.ndarray):
    if isinstance(data, pd.DataFrame):
        x_label, y_label = line_df(data, ax)
    elif isinstance(data, np.ndarray):
        if data.ndim == 1:
            x, y = np.arange(len(data)), data
        elif data.ndim == 2:
            x, y = data[:, 0], data[:, 1]
        elif data.T.ndim == 2:
            x, y = data.T[:, 0], data.T[:, 1]
        else:
            raise ValueError("data must be 1D or 2D")
        x_label, y_label = "x", "y"
        ax.plot(x, y, color="black", linewidth=0.8)
    else:
        raise TypeError(f"data type {type(data)} is not supported")
    return x_label, y_label


if __name__ == "__main__":
    path = "/test.csv"
    pd.read_csv(path, index_col=0)
