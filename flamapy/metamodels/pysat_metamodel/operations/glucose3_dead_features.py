from typing import Any

from pysat.solvers import Solver

from flamapy.core.operations import DeadFeatures
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3DeadFeatures(DeadFeatures):

    def __init__(self) -> None:
        self.dead_features: list[list[Any]] = []
        self.solver = Solver(name='glucose3')

    def get_dead_features(self) -> list[list[Any]]:
        return self.dead_features

    def get_result(self) -> list[list[Any]]:
        return self.get_dead_features()

    def execute(self, model: PySATModel) -> 'Glucose3DeadFeatures':

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        dead_features = []
        for variable in model.variables.items():
            if not self.solver.solve(assumptions=[variable[1]]):
                dead_features.append(variable[0])
        self.dead_features = dead_features
        self.solver.delete()
        return self
