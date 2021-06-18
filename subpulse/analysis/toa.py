"""Time of Arrival Analysis."""

import logging
import random
import warnings
from pathlib import Path
from typing import List

import numpy as np
from numba import jit
from numba.core.errors import NumbaPendingDeprecationWarning
from tqdm import tqdm

LOG_FORMAT: str = "[%(asctime)s] %(levelname)s "
LOG_FORMAT += "%(module)s::%(funcName)s():l%(lineno)d: "
LOG_FORMAT += "%(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.ERROR)
log = logging.getLogger(__name__)
# Suppress logging from stingray.lightcurve
logging.getLogger("lightcurve").setLevel(logging.ERROR)
# Supress deprecation messages
warnings.filterwarnings(action="ignore", category=DeprecationWarning)
warnings.filterwarnings(action="ignore", category=NumbaPendingDeprecationWarning)
warnings.filterwarnings(action="ignore", category=UserWarning)

FACTORIAL_LOOKUP_TABLE = np.array(
    [
        1,
        1,
        2,
        6,
        24,
        120,
        720,
        5040,
        40320,
        362880,
        3628800,
        39916800,
        479001600,
        6227020800,
        87178291200,
        1307674368000,
        20922789888000,
        355687428096000,
        6402373705728000,
        121645100408832000,
        2432902008176640000,
    ],
    dtype="int64",
)


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
    spacing = 1.0 / (samples * resolution)
    nyquist = 0.5 * (1.0 / resolution)
    return np.arange(
        spacing,
        nyquist + (spacing / oversample),
        (spacing / oversample),
    )


@jit(nopython=True)
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
    differences = np.zeros(len(toas) - 1)

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
    z1 = np.zeros(grid.size, dtype=np.float64)
    for index in np.arange(0, len(grid), 1):
        phase = pulse_phase(toas, grid[index])
        z1[index] = z_n(phase, n=1)
    return z1


@jit(nopython=True)
def pulse_phase(times, *frequency_derivatives):
    """
    Calculate pulse phase from the frequency and its derivatives.

    Parameters
    ----------
    times : array of floats
        The times at which the phase is calculated
    *frequency_derivatives: floats
        List of derivatives in increasing order, starting from zero.

    Returns
    -------
    phases : array of floats
        The absolute pulse phase
    """
    phase = np.zeros(len(times))
    for i_f, f in enumerate(frequency_derivatives):
        factorial = fast_factorial(i_f + 1)
        phase += 1 / factorial * times ** (i_f + 1) * f
    phase -= np.floor(phase)
    return phase


@jit(nopython=True)
def fast_factorial(value: np.int64) -> np.int64:
    """
    Factorial.

    Parameters
    ----------
    value : np.int64
        Some integer value.

    Returns
    -------
    np.int64

    Raises
    ------
    ValueError
        When value > 20.
    """
    if value > 20:
        raise ValueError("fast_factorial for n>20, not supported.")
    return FACTORIAL_LOOKUP_TABLE[value]


@jit(nopython=True)
def z_n(phase: np.ndarray, n: int = 2, norm: float = 1.0):
    """Z^2_n statistics, a` la Buccheri+03, A&A, 128, 245, eq. 2.

    Parameters
    ----------
    phase : array of floats
        The phases of the events
    n : int, default 2
        Number of harmonics, including the fundamental
    norm : float or array of floats
        A normalization factor that gets multiplied as a weight.

    Returns
    -------
    z2_n : float
        The Z^2_n statistics of the events.
    """
    nbin = len(phase)
    if nbin == 0:
        return 0
    normalization = np.array(norm)
    if normalization.size == 1:
        total_norm = nbin * normalization
    else:
        total_norm = np.sum(normalization)
    phase = phase * 2 * np.pi
    return 2.0 / total_norm * statistic(n, phase, normalization)


@jit(nopython=True)
def statistic(n, phase, norm):
    """Calculate Z^2 Statistic."""
    stat = np.zeros(n + 1, dtype=np.float64)
    for k in range(1, n + 1):
        stat[k - 1] = (
            np.sum(np.cos(k * phase) * norm) ** 2
            + np.sum(np.sin(k * phase) * norm) ** 2
        )
    return np.sum(stat)


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
    """
    Save np.ndarray.

    Parameters
    ----------
    data : np.ndarray
    savepath : Path
    """
    filename = savepath.absolute().as_posix()
    np.savez(filename, max_z12_power=data)
    savepath.chmod(0o777)


def execute(
    arrivals: List[float],
    chi: float,
    simulations: int,
    savepath: Path,
    debug: bool = False,
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
    max_z12_power = np.zeros(len(toas_mc))

    for index in tqdm(
        np.arange(0, len(toas_mc), 1),
        ascii=True,
        desc="simulating",
        leave=True,
    ):
        toa = toas_mc[index]
        error = errors_mc[index]
        z1 = z2search(toa, error, grid)
        max_index = np.argmax(z1)
        max_period = 1.0 / grid[max_index]  # noqa: F841
        max_z12_power[index] = z1[max_index]
    log.debug("Simulations: ✔️")
    save(max_z12_power, savepath)
    log.debug("Save: ✔️")
