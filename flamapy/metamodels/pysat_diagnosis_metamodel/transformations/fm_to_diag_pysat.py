import itertools
from typing import Any, List

from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models.feature_model import (
    FeatureModel,
    Constraint,
    Feature,
    Relation,
)
from flamapy.metamodels.pysat_diagnosis_metamodel.models.pysat_diagnosis_model import DiagnosisModel
from flamapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat

class FmToDiagPysat(FmToPysat):
    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'pysat_diagnosis'

    def __init__(self, source_model: FeatureModel) -> None:
        self.source_model = source_model
        self.counter = 1
        self.destination_model = DiagnosisModel()
        # self.r_cnf = self.destination_model.r_cnf
        # self.ctc_cnf = self.destination_model.ctc_cnf

    def add_root(self, feature: Feature) -> None:
        #self.r_cnf.append([self.destination_model.variables.get(feature.name)])
        self.destination_model.add_clause([self.destination_model.variables.get(feature.name)])
        print(self.destination_model.__class__)
        self.destination_model.add_clause_toMap(str(feature), [[self.destination_model.variables.get(feature.name)]])

    def _store_constraint_relation(self, relation: Relation, clauses:List[List[int]]) -> None:
        for clause in clauses:
            self.destination_model.add_clause(clause)
            self.destination_model.add_clause_toMap(str(relation), clauses)