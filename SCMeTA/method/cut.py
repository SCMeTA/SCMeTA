import matplotlib.pyplot as plt


def plot_xic(process, ref_mz):
    fig, ax = plt.subplots(figsize=(15, 5), dpi=100)
    xic = process.loc[process["Mass"] == ref_mz].drop("Mass", axis=1)
    ax.plot(xic.index, xic["Intensity"], linewidth=0.5)
    plt.show()


def cut_data(filename: str, process, cut_range: tuple[int, int] | None = None):
    if cut_range is None:
        cut_range = input(f"Cut {filename} range (start, end): ").split(",")
    return process.loc[cut_range[0] : cut_range[1]]
