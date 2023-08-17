import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.widgets import Button, RangeSlider


def cut_range_plot(lif: pd.DataFrame) -> (int, int):
    def f(x, range_):
        return x[range_[0] : range_[1]]

    init_start: int = 0
    init_end: int = len(lif["Time"])

    plt.style.use("fast")

    fig, axs = plt.subplots(2, 1, figsize=(10, 4))
    (line1,) = axs[0].plot(
        lif["Time"][init_start:init_end], lif["CH0"][init_start:init_end]
    )
    (line2,) = axs[1].plot(
        lif["Time"][init_start:init_end], lif["CH1"][init_start:init_end]
    )
    axs[0].set_title("CH0")
    axs[1].set_title("CH1")
    axs[1].set_xlabel("Time")
    fig.subplots_adjust(bottom=0.2)

    axrange = plt.axes([0.2, 0.075, 0.65, 0.03])
    srange = RangeSlider(
        axrange, "Range", 0, len(lif["Time"]), valinit=(init_start, init_end), valstep=1
    )

    def update(val):
        start = srange.val[0]
        end = srange.val[1]
        line1.set_data(lif["Time"][start:end], lif["CH0"][start:end])
        line2.set_data(lif["Time"][start:end], lif["CH1"][start:end])
        axs[0].set_ylim(
            [min(lif["CH0"][start:end]) - 500, max(lif["CH0"][start:end]) + 500]
        )
        axs[1].set_ylim(
            [min(lif["CH1"][start:end]) - 500, max(lif["CH1"][start:end]) + 500]
        )
        axs[0].set_xlim(
            [min(lif["Time"][start:end]) - 1, max(lif["Time"][start:end]) + 1]
        )
        axs[1].set_xlim(
            [min(lif["Time"][start:end]) - 1, max(lif["Time"][start:end]) + 1]
        )
        fig.canvas.draw_idle()

    srange.on_changed(update)

    resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
    button_reset = Button(resetax, "Reset", color="mistyrose", hovercolor="0.975")

    def reset(event):
        srange.reset()

    button_reset.on_clicked(reset)

    saveax = fig.add_axes([0.7, 0.025, 0.1, 0.04])
    button_save = Button(saveax, "Save", color="lavender", hovercolor="0.975")

    def save(event):
        plt.close()

    button_save.on_clicked(save)
    plt.show()
    return int(srange.val[0]), int(srange.val[1])
