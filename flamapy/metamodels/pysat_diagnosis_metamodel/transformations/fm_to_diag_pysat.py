from typing import Any

from flamapy.metamodels.fm_metamodel.models.feature_model import (
    FeatureModel,
    Constraint,
    Feature,
    Relation,
)

from flamapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat
from ..models.pysat_diagnosis_model import DiagnosisModel


class FmToDiagPysat(FmToPysat):
    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'pysat_diagnosis'

    def __init__(self, source_model: FeatureModel, cnf_method: str = 'distributive') -> None:
        super().__init__(source_model, cnf_method)
        self.destination_model = DiagnosisModel()

    def add_root(self, feature: Feature) -> None:
        var = self.destination_model.variables.get(feature.name)
        if var is None:
            raise KeyError(f'Feature {feature.name} not found in the model')

        self.destination_model.add_clause([var])
        self.destination_model.add_clause_to_map(str(feature), [[var]])

    #def _store_constraint_relation(self, relation: Relation, clauses: List[List[int]]) -> None:
    #    for clause in clauses:
    #        self.destination_model.add_clause(clause)
    #    self.destination_model.add_clause_to_map(str(relation), clauses)
    def add_relation(self, relation: Relation) -> None:
        if relation.is_mandatory():
            clauses = self._add_mandatory_relation(relation)
        elif relation.is_optional():
            clauses = self._add_optional_relation(relation)
        elif relation.is_or():
            clauses = self._add_or_relation(relation)
        elif relation.is_alternative():
            clauses = self._add_alternative_relation(relation)
        else:
            clauses = self._add_constraint_relation(relation)
        self._store_constraint_clauses(clauses)
        self.destination_model.add_clause_to_map(str(relation), clauses)

    def add_constraint(self, ctc: Constraint) -> None:
        if self.cnf_method == 'tseytin':
            clauses, aux_names = ctc.ast.get_clauses_with_aux(method='tseytin')
            aux_map = self._allocate_auxiliary(aux_names)
        else:
            clauses = ctc.ast.get_clauses()
            aux_map = {}

        def get_term_variable(term: Any) -> int:
            negated = term.startswith('-')
            name = term[1:] if negated else term
            var = aux_map[name] if name in aux_map else self.destination_model.get_variable(name)
            return -var if negated else var

        ctc_clauses = []
        for clause in clauses:
            clause_variables = list(map(get_term_variable, clause))
            ctc_clauses.append(clause_variables)
            self.destination_model.add_clause(clause_variables)

        self.destination_model.add_clause_to_map(str(ctc), ctc_clauses)
