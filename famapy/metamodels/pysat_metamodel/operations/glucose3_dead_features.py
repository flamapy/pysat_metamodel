from famapy.core.operations import DeadFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat.solvers import Glucose3


class Glucose3DeadFeatures(DeadFeatures):

    def __init__(self):
        self.dead_features = []

    def get_dead_features(self):
        return self.dead_features

    def get_result(self):
        return self.get_dead_features()

    def execute(self, model: PySATModel) -> 'Glucose3DeadFeatures':
        glucose = Glucose3()
        for clause in model.r_cnf:
            glucose.add_clause(clause)
        for clause in model.ctc_cnf:
            glucose.add_clause(clause)

        if glucose.solve():
            for feat in model.features:
                if not glucose.solve(assumptions = [-feat]):
                    self.core_features.append(model.features.get(feat))

        glucose.delete()
        return self
