from collections import deque

import pytest
import tatsu

from turingarena.cli.loggerinit import init_logger
from turingarena.protocol.algorithm import load_algorithm
from turingarena.protocol.exceptions import ProtocolError
from turingarena.protocol.model.model import InterfaceDefinition

init_logger()


def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock


def define_algorithms(interface_text, sources):
    for language, source in sources.items():
        with load_algorithm(
                source_text=source,
                language=language,
                interface_text=interface_text,
        ) as impl:
            yield impl


def parse_markers(interface_text):
    return tatsu.parse(
        """
            main = { ->(MARKER|$) }*;
            MARKER = /\s*/ '/*!' name:[/\w+/] '*/' /\s*/ ;
        """,
        interface_text,
        parseinfo=True,
    )


def compilation_fails(interface_text, message):
    markers = parse_markers(interface_text)
    with pytest.raises(ProtocolError) as excinfo:
        InterfaceDefinition.compile(interface_text)
    assert excinfo.value.message == message
    assert_at_markers(excinfo.value, markers)


def assert_at_markers(x, markers):
    start, end = markers
    (px, ps, pe) = map(lambda y: y.parseinfo, (x, start, end))
    assert px.pos == ps.endpos and px.endpos == pe.pos