from pysat.solvers import Glucose3

from famapy.core.operations import CoreFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3CoreFeatures(CoreFeatures):

    def __init__(self):
        self.core_features = ()

    def get_core_features(self):
        return self.core_features

    def get_result(self):
        return self.get_core_features()

    def execute(self, model: PySATModel) -> 'Glucose3CoreFeatures':
        g = Glucose3()
        for clause in model.cnf:  # AC es conjunto de conjuntos
            g.add_clause(clause)  # añadimos la constraint

        core_features = []
        if g.solve():
            for variable in model.variables.items():
                if not g.solve(assumptions=[-variable[1]]):
                    core_features.append(variable[0])
            
        self.core_features=core_features
        g.delete()
        return self
