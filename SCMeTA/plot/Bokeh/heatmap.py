from math import pi

import pandas as pd
import numpy as np

from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, PrintfTickFormatter
from bokeh.plotting import figure, show


def heatmap(mat_list: list[pd.DataFrame], title: str = "Heatmap"):
    """
    Plot a heatmap of the data

    Args:
        mat_list: list of dataframes
        title: title of the plot

    Returns:
        bokeh figure
    """
    mat = pd.concat(mat_list, axis=0).fillna(1)
    mat = mat.apply(np.log10)
    mat.reset_index(drop=True, inplace=True)
    mat["Scan"] = mat["Scan"].astype(str)
    mat = mat.set_index("Scan")
    mat.columns.name = "Mass"

    scan = mat.index
    mass = mat.columns

    df = pd.DataFrame(mat.stack(), columns=["Intensity"]).reset_index()

    mapper = LinearColorMapper(
        palette="Viridis256", low=df.Intensity.min(), high=df.Intensity.max()
    )

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

    p = figure(
        title=title,
        x_range=list(scan),
        y_range=list(mass),
        x_axis_location="above",
        width=900,
        height=900,
        tools=TOOLS,
        toolbar_location="below",
    )

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = pi / 3

    p.rect(
        x="Scan",
        y="Mass",
        width=1,
        height=1,
        source=df,
        fill_color={"field": "Intensity", "transform": mapper},
        line_color=None,
    )

    color_bar = ColorBar(
        color_mapper=mapper,
        major_label_text_font_size="5pt",
        ticker=BasicTicker(desired_num_ticks=len(df.Intensity.unique())),
        formatter=PrintfTickFormatter(format="%d"),
        label_standoff=6,
        border_line_color=None,
        location=(0, 0),
    )

    p.add_layout(color_bar, "right")

    show(p)
