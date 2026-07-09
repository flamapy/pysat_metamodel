"""SPL testing operations: covering arrays as a deliverable, coverage measurement, and
test-suite reduction.

``covering_array`` produces a reproducible t-wise covering array (a seed permutes the
coverage targets, so different seeds give different — equally valid — arrays).
``coverage`` measures which fraction of the satisfiable t-wise combinations an existing
configuration suite covers, and ``sample_reduction`` shrinks a suite while preserving the
t-wise coverage it already has. The two directions verify each other: a covering array
must measure 100% coverage.
"""
import random
import threading
from pathlib import Path
from typing import Any, Optional, cast

from pysat.solvers import Solver

from flamapy.core.exceptions import FlamaException
from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

from .pysat_twise_sampling import _satisfiable_targets, _to_configuration


def _feature_vars(model: PySATModel) -> list[int]:
    return (model.feature_variables() if hasattr(model, 'feature_variables')
            else list(model.features.keys()))


def _configuration_literals(model: PySATModel, configuration: Configuration) -> set[int]:
    """The full literal assignment a configuration induces (missing features = False)."""
    selected = {
        (name.name if hasattr(name, 'name') else str(name))
        for name, value in configuration.elements.items() if value
    }
    return {
        variable if name in selected else -variable
        for name, variable in model.variables.items()
    }


def _covered_targets(
    model: PySATModel, configurations: list[Configuration],
    targets: list[tuple[int, ...]],
) -> list[frozenset[tuple[int, ...]]]:
    per_configuration = []
    for configuration in configurations:
        literals = _configuration_literals(model, configuration)
        per_configuration.append(
            frozenset(target for target in targets if set(target) <= literals))
    return per_configuration


def _resolve_configurations(facade: Any, value: Any) -> list[Configuration]:
    """A list of configurations (paths/dicts/Configuration), or a directory of them."""
    if isinstance(value, str):
        path = Path(value)
        if not path.is_dir():
            raise FlamaException(
                f"'{value}' is not a directory of configuration files; pass either a "
                "directory path or a list of configurations.")
        value = sorted(str(item) for item in path.iterdir() if item.is_file())
    return [facade._as_configuration(item) for item in value]  # pylint: disable=protected-access


def _configurations_inputs(operation: Any, facade: Any, kwargs: dict[str, Any]) -> None:
    operation.set_configurations(_resolve_configurations(facade, kwargs['configurations']))
    if kwargs.get('t') is not None:
        operation.set_t(kwargs['t'])


class PySATCoveringArray(Operation):
    """A reproducible t-wise covering array of valid configurations."""

    facade = OperationDescriptor(
        doc=(
            'Returns a t-wise covering array: a set of valid configurations covering\n'
            'every satisfiable combination of ``t`` feature selections (pairwise for\n'
            '``t = 2``). ``seed`` permutes the coverage targets, making the array\n'
            'reproducible for a fixed seed and different across seeds.'
        ),
        returns='Union[None, List[Configuration]]',
        name='covering_array', operation='PySATCoveringArray', default_backend='sat',
        inputs=(
            Input('t', int, default=2, setter='set_t'),
            Input('seed', int, default=None, setter='set_seed'),
        ),
    )

    def __init__(self, t: int = 2, seed: Optional[int] = None) -> None:
        self.t = t
        self.seed = seed
        self.result: list[Configuration] = []
        self._interrupt_event: Optional[threading.Event] = None

    def set_interrupt_event(self, event: threading.Event) -> None:
        self._interrupt_event = event

    def set_t(self, t: int) -> None:
        self.t = t

    def set_seed(self, seed: int) -> None:
        self.seed = seed

    def get_result(self) -> list[Configuration]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATCoveringArray':
        sat_model = cast(PySATModel, model)
        clauses = list(sat_model.get_all_clauses().clauses)
        solver = Solver(name='glucose3', bootstrap_with=clauses)
        try:
            uncovered = _satisfiable_targets(solver, _feature_vars(sat_model), self.t)
            if self.seed is not None:
                random.Random(self.seed).shuffle(uncovered)

            configurations: list[Configuration] = []
            while uncovered:
                if self._interrupt_event is not None and self._interrupt_event.is_set():
                    break  # cooperative cancellation: return the partial array
                current: set[int] = set(uncovered[0])
                for target in uncovered[1:]:
                    if any(-literal in current for literal in target):
                        continue
                    tentative = current | set(target)
                    if solver.solve(assumptions=list(tentative)):
                        current = tentative
                solver.solve(assumptions=list(current))
                assignment = solver.get_model() or []
                configurations.append(_to_configuration(sat_model, assignment))
                satisfied = set(assignment)
                uncovered = [tg for tg in uncovered if not set(tg).issubset(satisfied)]
            self.result = configurations
        finally:
            solver.delete()
        return self


class PySATCoverage(Operation):
    """The t-wise coverage a configuration suite achieves."""

    facade = OperationDescriptor(
        doc=(
            'Measures the t-wise coverage of a configuration suite: the fraction of all\n'
            'satisfiable combinations of ``t`` feature selections that are covered by at\n'
            'least one of the given configurations (1.0 = full coverage).\n'
            '\n'
            '``configurations`` is a list of configurations (each a configuration file\n'
            'path, a ``{feature: value}`` mapping, or a Configuration object) or the path\n'
            'to a directory of configuration files.'
        ),
        returns='Union[None, float]',
        name='coverage', operation='PySATCoverage', default_backend='sat',
        inputs=(
            Input('configurations', Any, required=True, setter='set_configurations'),
            Input('t', int, default=2, setter='set_t'),
        ),
        input_adapter=_configurations_inputs,
    )

    def __init__(self, t: int = 2) -> None:
        self.t = t
        self.configurations: list[Configuration] = []
        self.result: float = 0.0

    def set_t(self, t: int) -> None:
        self.t = t

    def set_configurations(self, configurations: list[Configuration]) -> None:
        self.configurations = configurations

    def get_result(self) -> float:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATCoverage':
        sat_model = cast(PySATModel, model)
        solver = Solver(name='glucose3',
                        bootstrap_with=list(sat_model.get_all_clauses().clauses))
        try:
            targets = _satisfiable_targets(solver, _feature_vars(sat_model), self.t)
        finally:
            solver.delete()
        if not targets:
            self.result = 1.0
            return self
        covered: set[tuple[int, ...]] = set()
        for per_configuration in _covered_targets(sat_model, self.configurations, targets):
            covered |= per_configuration
        self.result = len(covered) / len(targets)
        return self


class PySATSampleReduction(Operation):
    """Greedy set-cover reduction of a suite, preserving its t-wise coverage."""

    facade = OperationDescriptor(
        doc=(
            'Reduces a configuration suite to a (greedily) minimal subset that preserves\n'
            'exactly the t-wise coverage the full suite already achieves.\n'
            '\n'
            '``configurations`` is a list of configurations (each a configuration file\n'
            'path, a ``{feature: value}`` mapping, or a Configuration object) or the path\n'
            'to a directory of configuration files.'
        ),
        returns='Union[None, List[Configuration]]',
        name='sample_reduction', operation='PySATSampleReduction', default_backend='sat',
        inputs=(
            Input('configurations', Any, required=True, setter='set_configurations'),
            Input('t', int, default=2, setter='set_t'),
        ),
        input_adapter=_configurations_inputs,
    )

    def __init__(self, t: int = 2) -> None:
        self.t = t
        self.configurations: list[Configuration] = []
        self.result: list[Configuration] = []

    def set_t(self, t: int) -> None:
        self.t = t

    def set_configurations(self, configurations: list[Configuration]) -> None:
        self.configurations = configurations

    def get_result(self) -> list[Configuration]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATSampleReduction':
        sat_model = cast(PySATModel, model)
        solver = Solver(name='glucose3',
                        bootstrap_with=list(sat_model.get_all_clauses().clauses))
        try:
            targets = _satisfiable_targets(solver, _feature_vars(sat_model), self.t)
        finally:
            solver.delete()
        per_configuration = _covered_targets(sat_model, self.configurations, targets)
        uncovered = set().union(*per_configuration) if per_configuration else set()

        chosen: list[int] = []
        while uncovered:
            best = max(range(len(per_configuration)),
                       key=lambda index: len(per_configuration[index] & uncovered))
            gained = per_configuration[best] & uncovered
            if not gained:
                break
            chosen.append(best)
            uncovered -= gained
        self.result = [self.configurations[index] for index in sorted(chosen)]
        return self
