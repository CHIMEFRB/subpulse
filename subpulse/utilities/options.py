import click
import ast


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
        except:
            raise click.BadParameter(value)
