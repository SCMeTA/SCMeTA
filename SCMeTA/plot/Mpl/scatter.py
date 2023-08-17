import numpy as np
import pandas as pd
from matplotlib.figure import Axes

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
    "red",
    "orange",
]


def scatter(
    data: np.ndarray | pd.DataFrame,
    ax: Axes,
    title: str,
    cell_range: dict[str, int] or None = None,
    point_size: int = 10,
):
    if isinstance(data, np.ndarray):
        if cell_range is None:
            ax.scatter(data[:, 0], data[:, 1], s=point_size, c=COLOR_KEY[0], label="data")
            ax.set_title(title)
        else:
            for i, (key, value) in enumerate(cell_range.items()):
                ax.scatter(
                    data[0 : value - 1, 0],
                    data[0 : value - 1, 1],
                    s=point_size,
                    c=COLOR_KEY[i],
                    label=key
                )
                data = data[value:]
    elif isinstance(data, pd.DataFrame):
        ax.scatter(data.iloc[:, 0], data.iloc[:, 1], s=point_size, c=COLOR_KEY[0], label="data")
    else:
        raise TypeError(f"data type {type(data)} is not supported")
    ax.set_title(title)
    ax.legend()


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    cell_range = {"A": 10, "B": 20, "C": 30, "D": 40, "E": 50, "F": 60, "G": 70, "H": 80, "I": 90, "J": 100}
    scatter(np.random.random((550, 2)), ax, "test", cell_range)
    fig.show()