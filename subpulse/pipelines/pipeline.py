"""Sample Pipeline."""

import logging
import os
import time
from pathlib import Path

import click

from subpulse.analysis import toa
from subpulse.utilities.options import PythonLiteralOption

LOG_FORMAT: str = "[%(asctime)s] %(levelname)s "
LOG_FORMAT += "%(module)s::%(funcName)s():l%(lineno)d: "
LOG_FORMAT += "%(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
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
    help="Unique ID for analysis bookeeping.",
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
@click.option(
    "--debug", help="Change logging level to debug.", default=False, type=click.BOOL
)
def run(
    event: int,
    arrivals: list,
    chi: float,
    simulations: int,
    fingerprint: int = int(time.time()),
    cluster: bool = False,
    job: int = 0,
    debug: bool = False,
) -> None:
    """Run single-thread subpulse analysis."""
    if os.environ.get("DEBUG", False) or debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.ERROR)

    click.echo("Running Subpulse TOA Analysis")
    click.echo(f"Parameters : {locals()}")
    click.echo(f"Fingerprint: {fingerprint}")
    click.echo(f"Log Level: {logging.getLevelName(log.level)}")

    if cluster:
        base_path = Path(
            f"/data/chime/intensity/processed/subpulse/{event}/{fingerprint}"
        )
        base_path.mkdir(parents=True, exist_ok=True)
        filename = (
            f"mc_{event}_nsim{simulations}_chi%.2f_{job}.npz" % chi
        )
    else:
        base_path = Path.cwd() / f"{event}/{fingerprint}"
        base_path.mkdir(parents=True, exist_ok=True)
        filename = (
            f"mc_{event}_nsim{simulations}_chi%.2f_{job}.npz" % chi
        )

    log.debug(f"Base Path: {base_path}")
    log.debug(f"Filename : {filename}")
    savepath = base_path.absolute().joinpath(filename)
    log.debug("TOA Analysis: Started...")
    toa.execute(arrivals, chi, simulations, savepath, debug)
    log.debug("TOA Analysis: Completed")


if __name__ == "__main__":
    run()
