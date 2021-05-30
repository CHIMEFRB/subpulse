"""Sample Pipeline."""
import click

import sys
sys.path.append("../analysis")
import toa

@click.command()
@click.option("--event", default=65777546, type=int)
@click.option("--arrivals", default=[], nargs=12, type=float)
@click.option("--chi", default=0.0, type=float)
@click.option("--processors", default=1, type=int)
@click.option("--simulations", default=1e6)
@click.option("--cluster", default=False, type=bool)

def run(event, arrivals, chi, processors, simulations, cluster):
    
    """Execute Analysis Routine."""
    simulations = int(simulations)
    toa.execute(event, arrivals, chi, processors, simulations, cluster)


if __name__ == "__main__":
    run()
