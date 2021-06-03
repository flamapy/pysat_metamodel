from famapy.core.operations import CoreFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat.solvers import Glucose3


class Glucose3CoreFeatures(CoreFeatures):

    def __init__(self):
        self.core_features = []

    def get_core_features(self):
        return self.core_features

    def get_result(self):
        return self.get_core_features()

    def execute(self, model: PySATModel) -> 'Glucose3CoreFeatures':
        glucose = Glucose3()

        for clause in model.r_cnf:
            glucose.add_clause(clause)
        for clause in model.ctc_cnf:
            glucose.add_clause(clause)

        if glucose.solve():
            for feat in model.features:
                if not glucose.solve(assumptions=[-feat]):
                    self.core_features.append(model.features.get(feat))

        glucose.delete()
        return self
