import os
import logging

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure, Axes

from SCMeTA.plot.Mpl import scatter, heatmap, line, radar, volcano, bar, box
from SCMeTA.method import round_rows, round_columns, k_w_test
from SCMeTA.method.machine_learning import discriminate, to_mat
from SCMeTA.file import SCData

logger = logging.getLogger(__name__)

FIGURE_SIZE = {
    "heatmap": (7, 5),
    "scatter": (5, 5),
    "line": (10, 5),
}


class MplPlot:
    def __init__(self):
        self.__data: dict[str, SCData] | None = None
        self.__mat: dict[str, pd.DataFrame] = {}
        self.__cell_range: dict[str, int] = {}

    def __read_csv(self, path: str):
        mat = pd.read_csv(path, index_col=0)
        name = os.path.basename(path).split(".")[0]
        self.__mat[name] = mat
        self.__cell_range[name] = mat.shape[0]
        logger.info(f"Successfully load {name}.")

    def load(self, data: dict[str, SCData] | None = None, path: str | None = None):
        if path is not None:
            # Load Cell Mat from dir or file
            if os.path.isdir(path):
                files = os.listdir(path)
                for file in files:
                    if file.endswith(".csv"):
                        self.__read_csv(os.path.join(path, file))
            elif os.path.isfile(path):
                self.__read_csv(path)
        elif data is not None:
            self.__data = data
            for name, ms_data in data.items():
                self.__mat[name] = ms_data.cell_mat
            logger.info("Successfully load data")
        else:
            raise ValueError("Please provide data or path")
        self.__cell_range = {key: mat.shape[0] for key, mat in self.__mat.items()}

    @staticmethod
    def init_plot(rows: int, cols: int, figure_type: str) -> tuple[Figure, Axes]:
        """
        Initialize a matplotlib figure and axes
        Args:
            rows: number of rows
            cols: number of columns
            figure_type: figure type
        Returns:
            fig: matplotlib figure
            ax: matplotlib axes
        """
        figsize = FIGURE_SIZE[figure_type]
        fig, ax = plt.subplots(
            nrows=rows,
            ncols=cols,
            figsize=(figsize[0] * cols, figsize[1] * rows),
            dpi=100,
        )
        return fig, ax

    def pca(self, ax=None, n_components: int = 2):
        full = discriminate(self.__mat, method="pca", n_components=n_components)
        if ax is None:
            fig, ax = self.init_plot(1, 1, "scatter")
        scatter(data=full, cell_range=self.__cell_range, ax=ax, title="PCA")
        return to_mat(full, self.__cell_range)

    def tsne(self, ax=None, n_components: int = 2):
        full = discriminate(self.__mat, method="tsne", n_components=n_components)
        if ax is None:
            fig, ax = self.init_plot(1, 1, "scatter")
        scatter(data=full, cell_range=self.__cell_range, ax=ax, title="t-SNE")
        return to_mat(full, self.__cell_range)

    def umap(self, ax=None, n_components: int = 2):
        full = discriminate(self.__mat, method="umap", n_components=n_components)
        if ax is None:
            fig, ax = self.init_plot(1, 1, "scatter")
        scatter(data=full, cell_range=self.__cell_range, ax=ax, title="UMAP")
        return to_mat(full, self.__cell_range)

    def scatter_select(self, method: list[str] | None = None, n_components: int = 2):
        if method is None:
            method = ["pca", "tsne", "umap"]
        fig, ax = self.init_plot(1, len(method), "scatter")
        for i, m in enumerate(method):
            if m == "pca":
                self.pca(ax[i], n_components)
            elif m == "tsne":
                self.tsne(ax[i], n_components)
            elif m == "umap":
                self.umap(ax[i], n_components)
            else:
                raise ValueError(f"method {m} is not supported")

    def heatmap(self, ax=None, fig=None, **kwargs):
        if ax is None:
            fig, ax = self.init_plot(1, 1, "heatmap")
        heatmap(
            self.__mat,
            cell_range=self.__cell_range,
            ax=ax,
            fig=fig,
            title="Heatmap",
            **kwargs,
        )

    def volcano(self, name1: str, name2: str, ax=None, **kwargs):
        mat1 = self.__mat[name1]
        mat2 = self.__mat[name2]
        if ax is None:
            fig, ax = self.init_plot(1, 1, "scatter")
        volcano(mat1, mat2, name1, name2, ax=ax, **kwargs)

    def box(self, ax=None, method: str = "tsne"):
        if ax is None:
            fig, ax = self.init_plot(1, 1, "scatter")
        full_data = discriminate(self.__mat, method=method, n_components=1)
        dict_data = to_mat(full_data, self.__cell_range, n_components=1)
        h_statistic, p_value = k_w_test(dict_data)
        box(dict_data, ax=ax, h_statistic=h_statistic, p_value=p_value)
        return dict_data

    # def radar(self, ax=None, mz_list: pd.DataFrame | None = None):
    #     if ax is None:
    #         fig, ax = self.init_plot(1, 1)
    #         radar(self.__mat, ax, self.__cell_range, title="Radar")
    #         return fig
    #     radar(self.__mat, ax, self.__cell_range, title="Radar")

    def ms_compare(self, name: str):
        fig, ax = self.init_plot(2, 1, "line")
        ms_data = self.__data[name]
        scan_list = ms_data.cell_pos.to_list()
        scan = int(input(f"Please Select a scan from:\n {scan_list}"))
        if scan not in scan_list:
            logger.warning(f"Scan {scan} is not in the scan list")
            raise ValueError(f"Scan {scan} is not in the scan list")
        line1 = round_columns(ms_data.get_scan(scan, data_type="raw"), axis=0)
        line2 = ms_data.get_scan(scan, data_type="cell_mat")
        full = pd.concat([line1, line2], axis=1).fillna(0)
        full.columns = ["Raw", "Process"]
        bar(full, ax=ax)
        return full

    def cell_compare(self, name: str):
        fig, ax = self.init_plot(2, 1, "line")
        ms_data = self.__data[name]
        cell_list = ms_data.cell_mat.index.tolist()
        cell1 = int(input(f"Please Select a cell from:\n {cell_list}"))
        cell2 = int(input(f"Please Select a cell from:\n {cell_list}"))
        if cell1 not in cell_list or cell2 not in cell_list:
            logger.warning(f"Cell {cell1} or {cell2} is not in the cell list")
            raise ValueError(f"Cell {cell1} or {cell2} is not in the cell list")
        line1 = ms_data.cell_mat.loc[cell1]
        line2 = ms_data.cell_mat.loc[cell2]
        full = pd.concat([line1, line2], axis=1).fillna(0)
        full.columns = [cell1, cell2]
        bar(full, ax=ax)
        return full
