import threading
from typing import Any, Iterator, Optional, cast

from pysat.solvers import Solver

from flamapy.core.operations import Configurations, StreamingOperation
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATConfigurations(Configurations, StreamingOperation):
    """Enumerates every valid configuration.

    Supports streaming (``iter_execute`` yields each configuration as the SAT solver
    produces it) and cooperative cancellation (the enumeration loop checks the interrupt
    event set by the execution engine and stops early with a partial result).
    """

    def __init__(self) -> None:
        self.result: list[Configuration] = []
        self.solver = Solver(name='glucose3')
        self._interrupt_event: Optional[threading.Event] = None

    def set_interrupt_event(self, event: threading.Event) -> None:
        self._interrupt_event = event

    def get_configurations(self) -> list[Configuration]:
        return self.get_result()

    def get_result(self) -> list[Configuration]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATConfigurations':
        sat_model = cast(PySATModel, model)
        self.result = list(
            iter_configurations(self.solver, sat_model, self._interrupt_event))
        return self

    def iter_execute(self, model: VariabilityModel) -> Iterator[Configuration]:
        sat_model = cast(PySATModel, model)
        for configuration in iter_configurations(
                self.solver, sat_model, self._interrupt_event):
            self.result.append(configuration)
            yield configuration


def iter_configurations(
    solver: Solver,
    model: PySATModel,
    interrupt_event: Optional[threading.Event] = None,
) -> Iterator[Configuration]:
    for clause in model.get_all_clauses():
        solver.add_clause(clause)
    try:
        for solutions in solver.enum_models():
            if interrupt_event is not None and interrupt_event.is_set():
                break
            product: dict[Any, bool] = {}
            for variable in solutions:
                if variable > 0:
                    name = model.features.get(variable)
                    if name is not None:  # skip auxiliary (Tseytin) variables
                        product[name] = True
            yield Configuration(product)
    finally:
        solver.delete()


def configurations(solver: Solver, model: PySATModel) -> list[Configuration]:
    return list(iter_configurations(solver, model))
