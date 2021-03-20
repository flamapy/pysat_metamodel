from pysat.solvers import Glucose3

from famapy.core.operations import DeadFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products


class Glucose3DeadFeatures(DeadFeatures):

    def __init__(self):
        self.dead_features = []

    def get_dead_features(self):
        return self.dead_features

    def get_result(self):
        return self.get_dead_features()

    def execute(self, model: PySATModel) -> 'Glucose3DeadFeatures':
        g = Glucose3()
        for clause in model.cnf:  # AC es conjunto de conjuntos
            g.add_clause(clause)  # añadimos la constraint

        dead_features = []
        for variable in model.variables.items():
            if not g.solve(assumptions=[variable[1]]):
                dead_features.append(variable[0])
            
        self.dead_features=dead_features
        g.delete()
        return self
