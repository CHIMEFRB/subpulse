"""Custom class for click option."""
import ast
import logging

import click

log = logging.getLogger(__name__)


class PythonLiteralOption(click.Option):
    """
    Class method to create a literal option .

    Parameters
    ----------
    click : click.Option
        Click Options Base Class.
    """

    def type_cast_value(self, ctx, value):
        """Cast value to a literal."""
        try:
            return ast.literal_eval(value)
        except Exception as error:
            log.error(error)
            raise click.BadParameter(value)
