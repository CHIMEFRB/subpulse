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

log = logging.getLogger(__name__)


@jit(nopython=True)
def frequency_grid(
    resolution: float = 0.32768 * 1.0e-3,
    samples: float = 250.0,
    oversample: int = 5,
) -> np.ndarray:
    """[summary]

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


@jit(nopython=True)
def parameters(
    arrivals: List[float],
    chi: float,
    processors: int,
    simulations: int = int(1e6),
):
    """[summary]

    Parameters
    ----------
    arrivals : List[float]
        [description]
    chi : float
        [description]
    processors : int
        [description]
    simulations : int, optional
        [description], by default 1e6

    Returns
    -------
    [type]
        [description]
    """
    workload = int(simulations / processors)
    # Convert
    toas = np.array(arrivals) * 0.001
    # np.empty is ~100x faster than np.zeros
    errors = np.zeros(len(toas)) * 0.001
    differences = np.empty(len(toas) - 1, dtype=float)

    for index in np.arange(0, len(toas) - 1, 1):
        differences[index] = toas[index + 1] - toas[index]

    minimum = chi * differences.mean()
    maximum = (2.0 - chi) * differences.mean()
    return workload, toas, errors, differences, minimum, maximum


def z2search(toas: np.ndarray, errors: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """[summary]

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
    """[summary]

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
    """[summary]

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
    differences_mc = np.empty((int(simulations), len(differences)))
    toas_mc = np.empty((int(simulations), len(differences) + 1))
    errors_mc = np.empty((int(simulations), len(differences) + 1))

    for index in np.arange(0, int(simulations), 1):
        differences_mc[index] = np.random.uniform(minimum, maximum, len(differences))

    for index in np.arange(0, len(differences_mc), 1):
        toas_mc[index, 1:] = np.cumsum(differences_mc[index, :])

    return differences_mc, toas_mc, errors_mc


def save(data: np.ndarray, savepath: Path) -> None:
    filename = savepath.absolute().as_posix()
    np.savez(filename, max_z12_power=data)


def execute(
    event: int,
    arrivals: List[float],
    chi: float,
    processors: int,
    simulations: int = int(1e6),
    cluster: bool = False,
    fingerprint: str = str(int(time.time())),
) -> None:
    """[summary]

    Parameters
    ----------
    event : int
        [description]
    arrivals : List[float]
        [description]
    chi : float
        [description]
    processors : int
        [description]
    simulations : int, optional
        [description], by default 1e6
    cluster : bool, optional
        [description], by default False
    fingerprint : str, optional
        id for each run, by default str(int(time.time()))
    """
    np.random.seed(quantumrandom.get_data()[0])
    grid = frequency_grid()
    workload, toas, errors, differences, minimum, maximum = parameters(
        arrivals=arrivals,
        chi=chi,
        processors=processors,
        simulations=simulations,
    )
    differences_mc, toas_mc, errors_mc = simulate(
        simulations, differences, minimum, maximum
    )
    max_z12_power = np.empty(len(toas_mc))

    for index in np.arange(0, len(toas_mc), 1):
        log.info(f"Simulation: {index}")
        toa = toas_mc[index]
        error = errors_mc[index]
        z1 = z2search(toa, error, grid)
        max_index = np.argmax(z1)
        max_period = 1.0 / grid[max_index]
        max_z12_power[index] = z1[max_index]

    filename = f"mc_{event}_nsim{simulations}_proc{processors}_chi{chi}.npz"

    if cluster:
        base_path = Path(f"/chime/intensity/processed/subpulse/{event}/{fingerprint}")
    else:
        base_path = Path(".")

    savepath = base_path.absolute().joinpath(
        f"mc_{event}_nsim{simulations}_proc{processors}_chi{chi}.npz"
    )
    save(max_z12_power, savepath)
