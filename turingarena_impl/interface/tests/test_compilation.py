from turingarena_impl.interface.common import Step
from turingarena_impl.interface.interface import InterfaceDefinition

# TODO: verify generated instructions
from turingarena_impl.interface.statements.call import MethodCallInstruction, MethodReturnInstruction


def test_read_scalar():
    interface = InterfaceDefinition.compile("""
        procedure p(a);
        main {
            read a;
            call p(a);
            checkpoint;
        }
    """)
    assert not interface.diagnostics()
    steps = interface.main_block.steps
    statements = interface.main_block.statements
    assert steps == [
        Step([
            statements[0],
            MethodCallInstruction(statements[1]),
        ]),
        Step([
            statements[2],
        ]),
    ]


def test_read_array_1():
    interface = InterfaceDefinition.compile("""
        procedure p(a[]);
        main {
            for i to 10 {
                read a[i];
            }
            call p(a);
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_read_array_2():
    interface = InterfaceDefinition.compile("""
        procedure p(a[][]);
        main {
            for i to 10 {
                for j to 10 {
                    read a[i][j];
                }
            }
            call p(a);
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_read_array_pass_slice():
    interface = InterfaceDefinition.compile("""
        procedure p(a[]);
        main {
            for i to 10 {
                for j to 10 {
                    read a[i][j];
                }
                call p(a[i]);
            }
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_write_scalar():
    interface = InterfaceDefinition.compile("""
        function f();
        main {
            call a = f();
            write a;
        }
    """)
    assert not interface.diagnostics()
    steps = interface.main_block.steps
    statements = interface.main_block.statements
    assert steps == [
        Step([
            MethodCallInstruction(statements[0]),
        ]),
        Step([
            MethodReturnInstruction(statements[0]),
            statements[1],
        ]),
    ]


def test_write_array_1():
    interface = InterfaceDefinition.compile("""
        function f();
        main {
            for i to 10 {
                call a[i] = f();
                write a[i];
            }
        }
    """)
    assert not interface.diagnostics()
