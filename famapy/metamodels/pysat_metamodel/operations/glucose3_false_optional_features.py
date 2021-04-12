from pysat.solvers import Glucose3

from famapy.core.operations import FalseOptionalFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

class Glucose3FalseOptionalFeatures(FalseOptionalFeatures):

    def __init__(self):
        self.false_optional_features = []

    def get_false_optional_features(self):
        return self.false_optional_features

    def get_result(self):
        return self.get_false_optional_features()

    def execute(self, model: PySATModel) -> 'Glucose3FalseOptionalFeatures':
        g_r = Glucose3()
        g_r_ctc = Glucose3()
        for clause in model.r_cnf:
            g_r.add_clause(clause)
            g_r_ctc.add_clause(clause)
        for clause in model.ctc_cnf:
            g_r_ctc.add_clause(clause)

        if g_r_ctc.solve():
            assumption = 1
            for feat in model.features:
                if not g_r_ctc.solve(assumptions=[-feat]) and g_r.solve(assumptions=[-feat]):
                    if g_r.solve(assumptions=[assumption,-feat]):
                        self.false_optional_features.append(model.features.get(feat))
                    assumption = feat

        g_r.delete()
        g_r_ctc.delete()
        return self
