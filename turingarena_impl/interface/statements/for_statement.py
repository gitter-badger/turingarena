import logging

from collections import namedtuple

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import Variable, ScalarType, VariableDeclaration, VariableAllocation


logger = logging.getLogger(__name__)


ForIndex = namedtuple("ForIndex", ["variable", "range"])


class ForStatement(Statement):
    __slots__ = []

    @property
    def index(self):
        return ForIndex(
            variable=Variable(value_type=ScalarType(int), name=self.ast.index),
            range=Expression.compile(self.ast.range, self.context),
        )

    @property
    def body(self):
        return Block(
            ast=self.ast.body,
            context=self.context.create_inner().with_index_variable(self.index),
        )

    @property
    def declared_variables(self):
        return tuple(
            VariableDeclaration(name=var.name, dimensions=var.dimensions, to_allocate=var.to_allocate - 1)
            for stmt in self.body.statements
            for var in stmt.declared_variables
            if var.to_allocate >= 0
        )

    @property
    def variables_to_allocate(self):
        return tuple(
            VariableAllocation(
                name=var.name,
                size=self.index.range.variable_name,
                dimensions=var.dimensions - var.to_allocate,
                indexes=tuple(
                    idx.variable.name
                    for idx in self.context.index_variables[1-var.to_allocate:]
                ) if var.to_allocate > 1 else ()
            )
            for stmt in self.body.statements
            for var in stmt.declared_variables
            if var.to_allocate > 0
        )

    def validate(self):
        yield from self.body.validate()

    def generate_instructions(self, context):
        if self.body.expects_request(None):
            yield SimpleForInstruction(statement=self, context=context)
        else:
            yield from self.do_generate_instruction(context)

    def do_generate_instruction(self, context):
        size = self.index.range.evaluate_in(context=context).get()
        for i in range(size):
            inner_context = context.child({self.index.variable.name: self.index.variable})
            inner_context.bindings[self.index.variable] = i
            yield from self.body.generate_instructions(inner_context)

    @property
    def context_after(self):
        return self.body.context_after

    def expects_request(self, request):
        return (
            request is None
            or self.body.expects_request(request)
        )


class SimpleForInstruction(Instruction, namedtuple("SimpleForInstruction", [
    "statement", "context"
])):
    """
    Corresponds to a for-loop which does not perform any function call.
    This is seen as a single instruction so that it can be fully skipped
    in the preflight phase, when the number of iterations is not yet known.
    """

    __slots__ = []

    def on_communicate_with_process(self, connection):
        for instruction in self.statement.do_generate_instruction(self.context):
            instruction.on_communicate_with_process(connection)