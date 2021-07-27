from typing import Any

from pysat.solvers import Glucose3

from famapy.core.operations import FalseOptionalFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3FalseOptionalFeatures(FalseOptionalFeatures):

    def __init__(self) -> None:
        self.false_optional_features: list[list[Any]] = []

    def get_false_optional_features(self) -> list[list[Any]]:
        return self.false_optional_features

    def get_result(self) -> list[list[Any]]:
        return self.get_false_optional_features()

    def execute(self, model: PySATModel) -> 'Glucose3FalseOptionalFeatures':
        glucose_r = Glucose3()
        glucose_r_ctc = Glucose3()
        for clause in model.r_cnf:
            glucose_r.add_clause(clause)
            glucose_r_ctc.add_clause(clause)
        for clause in model.ctc_cnf:
            glucose_r_ctc.add_clause(clause)

        if glucose_r_ctc.solve():
            assumption = 1
            for feat in model.features:
                if (
                    not glucose_r_ctc.solve(assumptions=[-feat]) and
                    glucose_r.solve(assumptions=[-feat])
                ):
                    if glucose_r.solve(assumptions=[assumption, -feat]):
                        self.false_optional_features.append(model.features.get(feat))
                    assumption = feat

        glucose_r.delete()
        glucose_r_ctc.delete()
        return self
