import pandas as pd

from bokeh.layouts import column
from bokeh.models import RangeTool
from bokeh.plotting import figure, show


def range_tool(process: pd.DataFrame, refer_mz: float) -> (int, int):
    xic = process.loc[process["Mass"] == refer_mz]
    xic.reset_index(inplace=True)
    start = xic["Scan"].min()
    end = xic["Scan"].max()
    p = figure(
        height=300,
        width=800,
        tools="xpan",
        toolbar_location=None,
        x_axis_type="datetime",
        x_axis_location="above",
        background_fill_color="#efefef",
        x_range=(start, end),
    )
    p.line("Scan", "Intensity", source=xic)
    p.yaxis.axis_label = "Intensity"

    select = figure(
        title="Drag the middle and edges of the selection box to change the range above",
        height=130,
        width=800,
        y_range=p.y_range,
        x_axis_type="datetime",
        y_axis_type=None,
        tools="",
        toolbar_location=None,
        background_fill_color="#efefef",
    )

    rt = RangeTool(x_range=p.x_range)
    rt.overlay.fill_color = "navy"
    rt.overlay.fill_alpha = 0.2

    select.line("Scan", "Intensity", source=xic)
    select.ygrid.grid_line_color = None
    select.add_tools(rt)
    select.toolbar.active_multi = rt

    show(column(p, select))
