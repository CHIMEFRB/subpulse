"""Subpulse plotting utilities."""
import click
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator


@click.command()
@click.option("-f", "--filename", type=str, required=True)
def plot(filename: str):
    """
    Plot subpulse statistics.

    Parameters
    ----------
    filename : str
        [description]
    """
    data = np.load(filename)
    max_z12_power = data["max_z12_power"]
    print(len(max_z12_power))
    fig = plt.figure()
    ax = fig.gca()
    nbins = 25
    binEdges = np.linspace(np.min(max_z12_power), np.max(max_z12_power), nbins + 1)
    hist, bins = np.histogram(max_z12_power, bins=binEdges)
    hist = hist.astype(float) / np.sum(hist)
    binWidth = bins[2] - bins[1]
    binCenter = np.divide(np.add(bins[:-1], bins[1:]), 2.0)

    ax.bar(
        binCenter,
        hist,
        align="center",
        width=binWidth,
        alpha=0.9,
        color="b",
        edgecolor="k",
    )

    detection_bar = 17.96141909472610009857
    ax.axvline(detection_bar, color="k", linestyle="--", linewidth=2.5)

    ax.set_yscale("log")

    ax.set_title(
        r"$\mathcal{N}_{\mathregular{sim}}$ = 10$^{\mathregular{6}}$ simultations ($\chi$ = 0.20)",  # noqa: E501
        fontsize=12.0,
        fontname="Helvetica",
    )
    ax.set_xlabel(
        r"Maximum $\mathregular{Z_1^2}$ Statistic", fontsize=12.0, fontname="Helvetica"
    )
    ax.set_ylabel(
        "Probability Density Function (PDF)", fontsize=12.0, fontname="Helvetica"
    )

    ax.text(
        detection_bar - 0.65,
        0.12,
        r"$\mathregular{Z}_{\mathregular{1}}^{\mathregular{2}}$ = 17.96 @ 217.3 ms",
        fontsize=12.0,
        color="k",
        rotation=90.0,
    )

    # Set minor tick axes.
    minorLocator_xaxis = AutoMinorLocator(2)
    ax.xaxis.set_minor_locator(minorLocator_xaxis)

    ax.get_xaxis().set_tick_params(
        direction="out", which="major", top=False, bottom=True, length=6.0
    )
    ax.get_xaxis().set_tick_params(
        direction="out", which="minor", top=False, bottom=True, length=3.0
    )
    ax.get_yaxis().set_tick_params(
        direction="in", which="major", left=True, right=True, length=6.0, pad=5.0
    )
    ax.get_yaxis().set_tick_params(
        direction="in", which="minor", left=True, right=True, length=3.0
    )

    ax_dummyx = ax.twiny()
    ax.axis(xmin=np.min(max_z12_power), xmax=np.max(max_z12_power))
    ax_dummyx.axis(xmin=np.min(max_z12_power), xmax=np.max(max_z12_power))
    ax_dummyx.get_xaxis().set_tick_params(
        direction="in", which="major", top=True, bottom=False, length=6.0
    )
    ax_dummyx.get_xaxis().set_tick_params(
        direction="in", which="minor", top=True, bottom=False, length=3.0
    )
    ax_dummyx.get_shared_x_axes().join(ax, ax_dummyx)
    ax_dummyx.set_xticklabels([])

    minorLocator_xaxis = AutoMinorLocator(2)
    ax_dummyx.xaxis.set_minor_locator(minorLocator_xaxis)
    idx = np.where(max_z12_power > detection_bar)[0]
    print(len(idx))
    plt.show()


if __name__ == "__main__":
    plot()
