import itertools
from typing import Any

from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models.feature_model import (
    FeatureModel,
    Constraint,
    Feature,
    Relation,
)
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat

class FmToDiagPysat(FmToPysat):
    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'pysat_diagnosys'

    def add_root(self, feature: Feature) -> None:
        #self.r_cnf.append([self.destination_model.variables.get(feature.name)])
        self.destination_model.add_clause([self.destination_model.variables.get(feature.name)])
        self.destination_model.add_clause_toMap(str(feature), [[self.destination_model.variables.get(feature.name)]])

    def _store_constraint_relation(self, relation: Relation, clauses:List[List[int]]) -> None:
        super._store_constraint_relation(relation, clauses)
        self.destination_model.add_clause_toMap(str(relation), clauses)