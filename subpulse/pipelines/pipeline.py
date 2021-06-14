"""Sample Pipeline."""
import logging
import os
import time
from pathlib import Path
from typing import Optional

import click
from chime_frb_api import frb_master

from subpulse.analysis import toa
from subpulse.utilities.options import PythonLiteralOption

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


@click.command()
@click.option("--event", help="CHIME/FRB Event Number", required=True, type=click.INT)
@click.option(
    "--arrivals",
    help="List of TOAs, e.g. '[0.01, 0.002]' ",
    cls=PythonLiteralOption,
    required=True,
)
@click.option("--chi", default=0.0, type=click.FLOAT)
@click.option(
    "--simulations",
    help="Number of total simulations to run.",
    default=int(1e8),
    required=False,
    type=click.INT,
)
@click.option(
    "--fingerprint",
    help="Unique ID for analysis run.",
    type=click.STRING,
    required=False,
)
@click.option(
    "--cluster",
    help="If running on the CHIME/FRB Cluster.",
    default=False,
    type=click.BOOL,
    required=False,
)
@click.option(
    "--job", help="Job Identification.", default=0, type=click.INT, required=False
)
@click.option("--debug", help="Logging Level", default=False, type=click.BOOL)
def run(
    event: int,
    arrivals: list,
    chi: float,
    simulations: int,
    fingerprint: Optional[int] = None,
    cluster: bool = False,
    job: int = 0,
    debug: bool = False,
) -> None:
    """
    Run single-thread subpulse analysis.

    Parameters
    ----------
    event : int
        CHIME/FRB Event Number
    arrivals : list
        Times of arrivials array.
    chi : float
        [description]
    simulations : int
        Number of simulations to be performed.
    fingerprint : Optional[str], optional
        UUID distinguish between different analysis runs, by default None
    cluster : bool, optional
        If running on the CHIME/FRB Cluster, by default False
    job : int, optional
        Job identificatio, by default 0
    """
    if os.environ.get("DEBUG", False) or debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARNING)

    click.echo("Running Subpulse TOA Analysis")
    click.echo(f"Parameters : {locals()}")
    if not fingerprint:
        fingerprint = int(time.time())
    click.echo(f"Fingerprint: {fingerprint}")
    click.echo(f"Log Level: {logging.getLevelName(log.level)}")

    if cluster:
        base_path = Path(f"/chime/intensity/processed/subpulse/{event}/{fingerprint}")
        base_path.mkdir(parents=True, exist_ok=True)
        filename = (
            f"mc_{event}_nsim{simulations}_chi{str(chi).replace('.','p')}_{job}.npz"
        )
    else:
        base_path = Path.cwd() / f"{event}/{fingerprint}"
        base_path.mkdir(parents=True, exist_ok=True)
        filename = (
            f"mc_{event}_nsim{simulations}_chi{str(chi).replace('.','p')}_{job}.npz"
        )

    log.debug(f"Base Path: {base_path}")
    log.debug(f"Filename : {filename}")
    savepath = base_path.absolute().joinpath(filename)
    log.debug("TOA Analysis: Started...")
    toa.execute(arrivals, chi, simulations, savepath)
    log.debug("TOA Analysis: Completed")


if __name__ == "__main__":
    run()


"""
python pipeline.py --event 65777546 --chi 0.2 --processors 1 --simulations 1e6 --cluster False --arrivals 0.000 439.018 653.038 1080.966 1304.422 1517.858 1733.211 1952.779 2170.596 2390.536 2603.326 3073.348"
"""
