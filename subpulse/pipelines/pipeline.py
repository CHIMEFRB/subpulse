"""Sample Pipeline."""
import sys

import click
from chime_frb_api import frb_master

from subpulse.analysis import toa


@click.command()
@click.option("--event", default=65777546, type=int)
@click.option("--arrivals", default=[], nargs=12, type=float)
@click.option("--chi", default=0.0, type=float)
@click.option("--processors", default=1, type=int)
@click.option("--simulations", default=1e6, type=int)
@click.option("--cluster", default=False, type=bool)
def run(
    event: int,
    arrivals: list,
    chi: float,
    processors: int,
    simulations: int,
    cluster: bool,
) -> None:
    """Run subpulse time of arrival analysis.

    Parameters
    ----------
    event : [type]
        [description]
    arrivals : [type]
        [description]
    chi : [type]
        [description]
    processors : [type]
        [description]
    simulations : [type]
        [description]
    cluster : [type]
        [description]
    """
    if not cluster:
        toa.execute(event, arrivals, chi, processors, simulations, cluster)
    else:
        master = frb_master.FRBMaster()
        for job in range(processors):
            response = master.swarm.spawn_job(
                job_name=f"subpulse-toa-{event}-{job}",
                image_name="chimefrb/subpulse",
                command=["python"],
                arguments=[
                    "--event",
                    f"{event}",
                    "--chi",
                    f"{chi}",
                    "--processors",
                    f"{processors}",
                    "--simulations",
                    f"{int(simulations)}",
                    "--cluster",
                    f"{cluster}",
                    "--arrivals",
                    f"{arrivals}",
                ],
            )


if __name__ == "__main__":
    run()
