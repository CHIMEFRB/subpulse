"""Sample Pipeline."""
import time
import click
from chime_frb_api import frb_master

from subpulse.analysis import toa
from subpulse.utilities.options import PythonLiteralOption


@click.command()
@click.option("--event", required=True, type=click.INT)
@click.option("--arrivals", cls=PythonLiteralOption, required=True)
@click.option("--chi", default=0.0, type=click.FLOAT)
@click.option("--jobs", default=1, type=click.INT)
@click.option("--simulations", default=int(1e8), type=click.INT)
def run(
    event: int,
    arrivals: list,
    chi: float,
    jobs: int,
    simulations: int,
) -> None:
    """
    Run the subpulse analysis.

    Parameters
    ----------
    event : int
        [description]
    arrivals : list
        [description]
    chi : float
        [description]
    jobs : int
        [description]
    simulations : int
        [description]
    """
    click.echo("Running Subpulse TOA Analysis")
    click.echo(f"Parameters : {locals()}")
    fingerprint = int(time.time())
    click.echo(f"Fingerprint: {fingerprint}")

    master = frb_master.FRBMaster()
    for job in range(jobs):
        response = master.swarm.spawn_job(
            job_name=f"subpulse-toa-{event}-{job}",
            image_name="chimefrb/subpulse",
            command=["python"],
            arguments=[
                "/src/subpulse/pipelines/pipeline.py",
                "--event",
                f"{event}",
                "--arrivals",
                f"{arrivals}",
                "--chi",
                f"{chi}",
                "--simulations",
                f"{int(simulations/jobs)}",
                "--fingerprint",
                f"{fingerprint}",
                "--cluster",
                True,
                "--job",
                job,
            ],
            job_cpu_limit=1,
            job_cpu_reservation=1,
        )
