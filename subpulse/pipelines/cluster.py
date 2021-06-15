"""Sample Pipeline."""
import time

import click
from chime_frb_api import frb_master

from subpulse.utilities.options import PythonLiteralOption


@click.command()
@click.option("--event", help="CHIME/FRB Event Number", required=True, type=click.INT)
@click.option(
    "--arrivals",
    help="List of TOAs, e.g. '[0.01, 0.002]' ",
    cls=PythonLiteralOption,
    required=True,
)
@click.option("--chi", default=0.0, show_default=True, type=click.FLOAT)
@click.option(
    "--simulations",
    help="Number of total simulations to run.",
    default=int(1e8),
    show_default=True,
    required=False,
    type=click.INT,
)
@click.option("--jobs", help="Number of jobs to spawn.", type=click.INT, required=True)
def run(
    event: int,
    arrivals: list,
    chi: float,
    jobs: int,
    simulations: int,
) -> None:
    """Run the subpulse analysis on the CHIME/FRB Cluster."""
    click.echo("Running Subpulse TOA Analysis")
    click.echo(f"Parameters : {locals()}")
    fingerprint = int(time.time())
    click.echo(f"Fingerprint: {fingerprint}")

    master = frb_master.FRBMaster()
    click.echo(f"Backend: {master.version()}")

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
                f"{True}",
                "--job",
                f"{job}",
            ],
            job_cpu_limit=1,
            job_cpu_reservation=1,
        )
