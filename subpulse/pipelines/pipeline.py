"""Sample Pipeline."""
import click

from subpulse.routines import composite


@click.command()
@click.option("--minimum", default=0.1)
@click.option("--maximum", default=10.0)
def run(minimum, maximum):
    """Execute Analysis Routine."""
    analysis = composite.Composite(maximum=maximum, minimum=minimum)
    print(analysis.seedling())
    print(analysis.get_alpha())


if __name__ == "__main__":
    run()
