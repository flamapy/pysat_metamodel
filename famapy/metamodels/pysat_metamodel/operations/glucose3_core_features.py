from pysat.solvers import Glucose3

from famapy.core.operations import CoreFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

class Glucose3CoreFeatures(CoreFeatures):

    def __init__(self):
        self.core_features = []

    def get_core_features(self):
        return self.core_features

    def get_result(self):
        return self.get_core_features()

    def execute(self, model: PySATModel) -> 'Glucose3CoreFeatures':
        g = Glucose3()
        for clause in model.r_cnf:
            g.add_clause(clause)
        for clause in model.ctc_cnf:
            g.add_clause(clause)

        if g.solve():
            for feat in model.features:
                if not g.solve(assumptions=[-feat]):
                    self.core_features.append(model.features.get(feat))

        g.delete()
        return self
