import argparse
import sys


class ArgumentParserForBlender(argparse.ArgumentParser):
    """A subclass of ArgumentParser that allows blender to parse arguments.

    Args:
        argparse (argparse.ArgumentParser): The base ArgumentParser class.
    """

    def _get_argv_after_doubledash(self):
        """Returns the arguments after the double dash (--).

        Returns:
            list: The arguments after the double dash (--).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx + 1 :]
        except ValueError as e:
            return []

    def parse_args(self):
        """Parses the arguments after the double dash (--)."""
        return super().parse_args(args=self._get_argv_after_doubledash())
