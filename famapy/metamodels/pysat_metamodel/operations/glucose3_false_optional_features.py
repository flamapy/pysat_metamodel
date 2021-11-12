from typing import Any

from pysat.solvers import Glucose3

from famapy.core.operations import FalseOptionalFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3FalseOptionalFeatures(FalseOptionalFeatures):

    def __init__(self, optional_features: list[str]) -> None:
        self.result: list[Any] = []
        self.optional_features = optional_features

    def execute(self, model: PySATModel) -> 'Glucose3FalseOptionalFeatures':
        self.result = get_false_optional_features(model, self.optional_features)
        return self

    def get_false_optional_features(self) -> list[list[Any]]:
        return self.get_result()

    def get_result(self) -> list[Any]:
        return self.result


def get_false_optional_features(model: PySATModel, optional_features: list[str]) -> list[Any]:
    result = []
    solver = Glucose3()
    for clause in model.get_all_clauses():
        solver.add_clause(clause)
    
    for feature in optional_features:
        variable = model.variables.get(feature)
        assert variable is not None
        satisfiable = solver.solve(assumptions=[-variable])
        if not satisfiable:
            result.append(feature)
    solver.delete()
    return result
