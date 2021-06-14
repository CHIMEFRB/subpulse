import logging
import time
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import quantumrandom
import stingray.lightcurve as lightcurve
import stingray.pulse.pulsar as plsr
from numba import jit

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


@jit(nopython=True)
def frequency_grid(
    resolution: float = 0.32768 * 1.0e-3,
    samples: float = 250.0,
    oversample: int = 5,
) -> np.ndarray:
    """
    Generate frequency grid.

    Parameters
    ----------
    resolution : float, optional
        [description], by default 0.32768*1.0e-3
    samples : float, optional
        [description], by default 250.0
    oversample : int, optional
        [description], by default 5

    Returns
    -------
    np.ndarray
        [description]
    """
    duration = samples * resolution
    spacing = 1.0 / duration
    sampling = 1.0 / resolution
    nyquist = 0.5 * sampling
    return np.arange(
        spacing,
        nyquist + (spacing / oversample),
        (spacing / oversample),
    )


def parameters(
    arrivals: List[float],
    chi: float,
    simulations: int = int(1e6),
):
    """
    Calculate the parameters for the workload .

    Parameters
    ----------
    arrivals : List[float]
        [description]
    chi : float
        [description]
    processors : int
        [description]
    simulations : int, optional
        [description], by default int(1e6)

    Returns
    -------
    [type]
        [description]
    """
    # Convert
    toas = np.array(arrivals) * 0.001
    # np.empty is ~100x faster than np.zeros
    errors = np.zeros(len(toas)) * 0.001
    differences = np.zeros(len(toas) - 1, dtype=float)

    for index in np.arange(0, len(toas) - 1, 1):
        differences[index] = toas[index + 1] - toas[index]

    minimum = chi * differences.mean()
    maximum = (2.0 - chi) * differences.mean()
    return toas, errors, differences, minimum, maximum


def z2search(toas: np.ndarray, errors: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """
    Lightcurve search.

    Parameters
    ----------
    toas : np.ndarray
        [description]
    errors : np.ndarray
        [description]
    grid : np.ndarray
        [description]

    Returns
    -------
    np.ndarray
        [description]
    """
    lc = lightcurve.Lightcurve(toas, np.ones(len(toas)), err=errors)
    z1 = np.empty(grid.size, dtype=float)
    for index in np.arange(0, len(grid), 1):
        phase = plsr.pulse_phase(lc.time, grid[index])
        z1[index] = plsr.z_n(phase, n=1)
    return z1


def plot(z1: np.ndarray, grid: np.ndarray) -> None:
    """
    Plot a 2D array of z1 and grid .

    Parameters
    ----------
    z1 : np.ndarray
        [description]
    grid : np.ndarray
        [description]
    """
    plt.figure()
    plt.plot(np.divide(1.0, grid), z1)
    plt.show()


@jit(nopython=True)
def simulate(simulations: int, differences: np.ndarray, minimum: int, maximum: int):
    """
    Generate simulated observations.

    Parameters
    ----------
    simulations : int
        [description]
    differences : np.ndarray
        [description]
    minimum : int
        [description]
    maximum : int
        [description]

    Returns
    -------
    [type]
        [description]
    """
    differences_mc = np.zeros((int(simulations), len(differences)))
    toas_mc = np.zeros((int(simulations), len(differences) + 1))
    errors_mc = np.zeros((int(simulations), len(differences) + 1))

    for index in np.arange(0, int(simulations), 1):
        differences_mc[index] = np.random.uniform(minimum, maximum, len(differences))

    for index in np.arange(0, len(differences_mc), 1):
        toas_mc[index, 1:] = np.cumsum(differences_mc[index, :])

    return differences_mc, toas_mc, errors_mc


def save(data: np.ndarray, savepath: Path) -> None:
    filename = savepath.absolute().as_posix()
    np.savez(filename, max_z12_power=data)


def execute(
    arrivals: List[float],
    chi: float,
    simulations: int,
    savepath: Path,
    debug: bool = True,
) -> None:
    """
    Run the simulation .

    Parameters
    ----------
    arrivals : List[float]
        [description]
    chi : float
        [description]
    processors : int
        [description]
    simulations : int
        [description]
    savepath: str
        [description]
    """
    if debug:
        log.setLevel(logging.DEBUG)
    log.debug("Job Recieved: ✔️")
    # np.random.seed(quantumrandom.get_data()[0])
    import random

    np.random.seed(random.SystemRandom().randint(0, 2147483647))
    log.debug("Random Seed : ✔️")
    grid = frequency_grid()
    log.debug("Frequency Grid: ✔️")
    toas, errors, differences, minimum, maximum = parameters(
        arrivals=arrivals,
        chi=chi,
        simulations=simulations,
    )
    log.debug("Parameters: ✔️")
    differences_mc, toas_mc, errors_mc = simulate(
        simulations, differences, minimum, maximum
    )
    log.debug("Dataset: ✔️")
    max_z12_power = np.empty(len(toas_mc))

    for index in np.arange(0, len(toas_mc), 1):
        log.debug(f"Simulation: {index}")
        toa = toas_mc[index]
        error = errors_mc[index]
        z1 = z2search(toa, error, grid)
        max_index = np.argmax(z1)
        max_period = 1.0 / grid[max_index]
        max_z12_power[index] = z1[max_index]
    log.debug("Simulations: ✔️")
    save(max_z12_power, savepath)
    log.debug("Save: ✔️")
