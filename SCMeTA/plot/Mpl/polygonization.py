import numpy as np
import pandas as pd
from matplotlib.widgets import PolygonSelector
from matplotlib.path import Path
import matplotlib.pyplot as plt


class SelectFromCollection:
    def __init__(self, ax, collection, alpha_other=0.3):
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.alpha_other = alpha_other

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError("Collection must have a facecolor")
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (self.Npts, 1))

        self.poly = PolygonSelector(ax, self.onselect)
        self.ind = []

    def onselect(self, verts):
        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

    def disconnect(self):
        self.poly.disconnect_events()
        self.fc[:, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()


def polygonize(
    mat_list: list[pd.DataFrame], m1=732.55, m2=760.58
) -> list[pd.DataFrame]:
    mat = pd.concat(mat_list).reset_index()
    range_list = [mat.shape[0] for mat in mat_list]
    fig, ax = plt.subplots()
    pts = ax.scatter(mat.loc[:, m1], mat.loc[:, m2])
    selector = SelectFromCollection(ax, pts)
    fig.show()
    selector.disconnect()
    select_list = []
    for index, i in enumerate(range_list):
        if index == 0:
            offset_lower = 0
            offset_higher = i
        else:
            offset_lower = offset_higher
            offset_higher = offset_lower + i
        select_list.append(
            [x for x in selector.ind if (x < offset_higher) and (x >= offset_lower)]
        )
    return [mat.iloc[select] for select, mat in zip(select_list, mat_list)]
