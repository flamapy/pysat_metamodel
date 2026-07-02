from flamapy.metamodels.fm_metamodel.models import FeatureModel, ClauseSet
from flamapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat
from ..models.pysat_diagnosis_model import DiagnosisModel


class FmToDiagPysat(FmToPysat):
    """Like FmToPysat, but into a DiagnosisModel that also keeps a clause → constraint map.

    The CNF and its per-source clause grouping both come from the shared feature-model encoder
    (``ClauseSet``); this transformation just wraps them into the diagnosis model.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'pysat_diagnosis'

    def __init__(self, source_model: FeatureModel, cnf_method: str = 'distributive') -> None:
        super().__init__(source_model, cnf_method)
        self.destination_model = DiagnosisModel()

    def transform(self) -> DiagnosisModel:
        clause_set = ClauseSet.from_feature_model(self.source_model, cnf_method=self.cnf_method)
        model = self.destination_model
        for clause in clause_set.clauses:
            model.add_clause(clause)
        model.variables = dict(clause_set.variables)
        model.features = dict(clause_set.features)
        model.auxiliary_variables = set(clause_set.auxiliary_variables)
        model.original_model = self.source_model
        # Clause → constraint mapping (root feature / relations / cross-tree constraints).
        for description, clauses in clause_set.clause_groups:
            model.add_clause_to_map(description, clauses)
        return model
