import pytest

from turingarena.cli import docopt_cli


@docopt_cli
def test_cli(args):
    """
    Usage:
        test <pytestargs>...

    Options:
        <pytestargs>  Options to pass to pytest
    """
    return pytest.main(args["<pytestargs>"])
