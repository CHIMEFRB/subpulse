import multiprocessing as mp
import threading
import time
from multiprocessing import Process
from threading import Thread
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import quantumrandom
import stingray.lightcurve as lightcurve
import stingray.pulse.pulsar as plsr
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.modeling import fitting, models
from astropy.modeling.functional_models import Gaussian2D
from numba import jit
from scipy import signal
from scipy.signal import argrelextrema
from stingray.utils import poisson_symmetrical_errors


def frequency_grid(
    resolution: float = 0.32768 * 1.0e-3,
    samples: float = 250.0,
    oversample: int = 5,
) -> np.ndarray:
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
    processors: int,
    simulations: int = 1e6,
):
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
    lc = lightcurve.Lightcurve(toas, np.ones(len(toas)), err=errors)
    z1 = np.empty(grid.size, dtype=float)
    for index in np.arange(0, len(grid), 1):
        phase = plsr.pulse_phase(lc.time, grid[index])
        z1[index] = plsr.z_n(phase, n=1)
    return z1


def plot(z1: np.ndarray, grid: np.ndarray) -> None:
    plt.figure()
    plt.plot(np.divide(1.0, grid), z1)
    plt.show()


@jit(nopython=True)
def simulate(simulations: int, differences: np.ndarray, minimum: int, maximum: int):
    differences_mc = np.empty((int(simulations), len(differences)))
    toas_mc = np.empty((int(simulations), len(differences) + 1))
    errors_mc = np.empty((int(simulations), len(differences) + 1))

    for index in np.arange(0, int(simulations), 1):
        differences_mc[index] = np.random.uniform(minimum, maximum, len(differences))

    for index in np.arange(0, len(differences_mc), 1):
        for pointer in np.arange(0, len(differences_mc[index]) + 1, 1):
            toas_mc[index, 1:] = np.cumsum(differences_mc[index, 0:pointer])
    return differences_mc, toas_mc, errors_mc


def save(data: np.ndarray, filename: str) -> None:
    np.savez(filename, max_z12_power=data)


def execute(
    event: int,
    arrivals: List[float],
    chi: float,
    processors: int,
    simulations: int = 1e6,
    cluster: bool = False,
):
    np.random.seed(quantumrandom.get_data()[0])
    grid = frequency_grid()
    workload, toas, errors, differences, minimum, maximum = parameters(
        arrivals=arrivals,
        chi=chi,
        processors=processors,
        simulations=simulations,
    )
    differences_mc, toas_mc, errors_mc = simulate(simulations, differences, minimum, maximum)
    max_z12_power = np.empty(len(toas_mc))

    for index in np.arange(0, len(toas_mc), 1):
        toa = toas_mc[index]
        error = errors_mc[index]
        z1 = z2search(toa, error, grid)
        max_index = np.argmax(z1)
        max_period = 1.0 / grid[max_index]
        max_z12_power[index] = z1[max_index]
    
    if (cluster == True):
        # TODO: Proper filepath on cluster / home computer
        # /chime/intensity/processed/<subpulse>/<event_number>/<chi>/<name.npz>
        pass
    else:
        filename = f"mc_{event}_s{simulations}_p{processors}.npz"
        save(max_z12_power, filename)
