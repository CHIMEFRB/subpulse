"""Monitor jobs."""
import click
from chime_frb_api import frb_master


@click.command()
@click.option(
    "--job-name",
    "-j",
    help="Regex pattern for jobs to monitor.",
    default="subpulse-toa",
)
def monitor(job_name: str):
    """Monitor jobs."""
    master = frb_master.FRBMaster()
    master.swarm.monitor_jobs("subpulse-toa")


if __name__ == "__main__":
    monitor()
