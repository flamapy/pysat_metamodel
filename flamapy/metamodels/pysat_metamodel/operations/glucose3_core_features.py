from typing import Any

from pysat.solvers import Glucose3

from flamapy.core.operations import CoreFeatures
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3CoreFeatures(CoreFeatures):

    def __init__(self) -> None:
        self.core_features: list[list[Any]] = []

    def get_core_features(self) -> list[list[Any]]:
        return self.core_features

    def get_result(self) -> list[list[Any]]:
        return self.get_core_features()

    def execute(self, model: PySATModel) -> 'Glucose3CoreFeatures':
        glucose = Glucose3()
        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            glucose.add_clause(clause)  # añadimos la constraint

        core_features = []
        if glucose.solve():
            for variable in model.variables.items():
                if not glucose.solve(assumptions=[-variable[1]]):
                    core_features.append(variable[0])

        self.core_features = core_features
        glucose.delete()
        return self
