from bokeh.io import output_notebook

from SCMeTA.plot.Bokeh import heatmap
from SCMeTA.file import SCData


class BokehPlot:
    def __init__(self, data: dict[str, SCData]):
        self.__data = [d.cell_mat for d in data.values()]
        self.__data_count = len(data)
        self.__cell_range = {
            key: value.cell_mat.shape[0] for key, value in data.items()
        }
        output_notebook()

    def heatmap(self, title: str = "Heatmap", **kwargs):
        heatmap(mat_list=self.__data, title=title)
