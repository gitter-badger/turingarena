from __future__ import print_function

import os
from argparse import ArgumentParser

from turingarena_cli.common import init_logger
from turingarena_cli.daemonctl import DAEMON_CONTROL_PARSER
from turingarena_cli.evaluate import EvaluateCommand
from turingarena_cli.files import FILE_PARSER
from turingarena_cli.legacy import INFO_PARSER, TEST_PARSER, BASE_MAKE_PARSER, MAKE_PARSER
from turingarena_cli.new import NewCommand
# in python2.7, quote is in pipes and not in shlex
from turingarena_cli.remote import RemoteExecCommand

try:
    from shlex import quote
except ImportError:
    from pipes import quote

# PYTHON_ARGCOMPLETE_OK
try:
    import argcomplete
except ImportError:
    pass

PARSER = ArgumentParser()

subparsers = PARSER.add_subparsers(dest="command", metavar="COMMAND")
subparsers.required = True

subparsers.add_parser(
    "evaluate",
    parents=[EvaluateCommand.PARSER],
    help=EvaluateCommand.PARSER.description,
)
subparsers.add_parser(
    "info",
    parents=[INFO_PARSER],
    help=INFO_PARSER.description,
)
subparsers.add_parser(
    "test",
    parents=[TEST_PARSER],
    help=TEST_PARSER.description,
)
subparsers.add_parser(
    "new",
    parents=[NewCommand.PARSER],
    help=NewCommand.PARSER.description,
)
subparsers.add_parser(
    "file",
    parents=[FILE_PARSER],
    help=FILE_PARSER.description,
)
subparsers.add_parser(
    "make",
    parents=[MAKE_PARSER],
    help=MAKE_PARSER.description,
)
subparsers.add_parser(
    "skeleton",
    parents=[BASE_MAKE_PARSER],
    help="generate skeleton",
)
subparsers.add_parser(
    "template",
    parents=[BASE_MAKE_PARSER],
    help="generate template",
)
subparsers.add_parser(
    "daemon",
    parents=[DAEMON_CONTROL_PARSER],
    help=DAEMON_CONTROL_PARSER.description,
)
subparsers.add_parser(
    "exec",
    parents=[RemoteExecCommand.PARSER],
    help=RemoteExecCommand.PARSER.description,
).set_defaults(Command=RemoteExecCommand)


def main():
    try:
        argcomplete.autocomplete(PARSER)
    except NameError:
        pass
    args = PARSER.parse_args()

    init_logger(args.log_level)

    command = args.Command(args=args, cwd=os.curdir)
    command.run()
