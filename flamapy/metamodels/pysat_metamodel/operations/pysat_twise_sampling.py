import itertools
from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class PySATTWiseSampling(Operation):
    """t-wise (combinatorial) sampling: a set of valid configurations that covers every
    satisfiable combination of ``t`` feature selections.

    For ``t = 2`` this yields a pairwise covering sample. The sample is built greedily:
    each configuration is grown to cover as many still-uncovered feature combinations as
    the constraints allow.
    """

    facade = OperationDescriptor(
        name='t_wise_sampling', operation='PySATTWiseSampling', default_backend='sat',
        selectable_backend=True,
        inputs=(Input('t', int, default=2, setter='set_t'),),
    )

    def __init__(self, t: int = 2) -> None:
        self.t = t
        self.result: list[Configuration] = []

    def set_t(self, t: int) -> None:
        self.t = t

    def get_sample(self) -> list[Configuration]:
        return self.result

    def get_result(self) -> list[Configuration]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATTWiseSampling':
        sat_model = cast(PySATModel, model)
        self.result = _twise_sample(sat_model, self.t)
        return self


def _satisfiable_targets(solver: Solver, feature_vars: list[int], t: int) -> list[tuple[int, ...]]:
    """Every satisfiable combination of ``t`` feature variables with each sign pattern."""
    targets: list[tuple[int, ...]] = []
    for combination in itertools.combinations(feature_vars, t):
        for signs in itertools.product((1, -1), repeat=t):
            literals = tuple(sign * var for sign, var in zip(signs, combination))
            if solver.solve(assumptions=list(literals)):
                targets.append(literals)
    return targets


def _twise_sample(model: PySATModel, t: int) -> list[Configuration]:
    clauses = list(model.get_all_clauses().clauses)
    solver = Solver(name='glucose3', bootstrap_with=clauses)
    feature_vars = model.feature_variables() if hasattr(model, 'feature_variables') \
        else list(model.features.keys())

    uncovered = _satisfiable_targets(solver, feature_vars, t)
    configurations: list[Configuration] = []

    while uncovered:
        current: set[int] = set(uncovered[0])
        # Greedily merge other uncovered targets that stay jointly satisfiable.
        for target in uncovered[1:]:
            if any(-literal in current for literal in target):
                continue
            tentative = current | set(target)
            if solver.solve(assumptions=list(tentative)):
                current = tentative
        solver.solve(assumptions=list(current))
        assignment = solver.get_model() or []
        configurations.append(_to_configuration(model, assignment))
        satisfied = set(assignment)
        uncovered = [tg for tg in uncovered if not set(tg).issubset(satisfied)]

    solver.delete()
    return configurations


def _to_configuration(model: PySATModel, assignment: list[int]) -> Configuration:
    elements: dict[Any, Any] = {}
    for literal in assignment:
        if literal > 0:
            name = model.features.get(literal)
            if name is not None:  # skip auxiliary variables
                elements[name] = True
    return Configuration(elements)
