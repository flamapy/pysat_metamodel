from pysat.solvers import Glucose3

from famapy.core.operations import FalseOptionalFeatures
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_core_features import Glucose3CoreFeatures


class Glucose3FalseOptionalFeatures(FalseOptionalFeatures):

    def __init__(self):
        self.false_optional_features = []

    def get_false_optional_features(self):
        return self.false_optional_features

    def get_result(self):
        return self.get_false_optional_features()

    def execute(self, pysat_model: PySATModel) -> 'Glucose3FalseOptionalFeatures':
        g_complete = Glucose3()
        for clause in pysat_model.cnf:  # AC es conjunto de conjuntos
            g_complete.add_clause(clause)  # añadimos la constraint

        g_partial = Glucose3()
        for clause in pysat_model.partial_cnf:  # AC es conjunto de conjuntos
            g_partial.add_clause(clause)  # añadimos la constraint

        core_features = []
        if g_complete.solve():
            for variable in pysat_model.variables.items():
                if not g_complete.solve(assumptions=[-variable[1]]):
                    core_features.append(variable[0])

        partial_core_features = []
        if g_partial.solve():
            for variable in pysat_model.variables.items():
                if not g_partial.solve(assumptions=[-variable[1]]):
                    partial_core_features.append(variable[0])

        false_optional = []
        for feat in core_features:
            if feat not in partial_core_features:
                false_optional.append(feat)
            
        self.false_optional_features=false_optional
        g_complete.delete()
        g_partial.delete()
        return self
