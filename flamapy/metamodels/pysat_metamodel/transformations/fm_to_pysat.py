from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel, ClauseSet
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class FmToPysat(ModelToModel):
    """Transform a feature model into a python-sat ``PySATModel``.

    The feature-model → CNF encoding lives in ``fm_metamodel`` (``ClauseSet.from_feature_model``);
    this class just wraps the resulting clause set into the python-sat-backed ``PySATModel`` so the
    SAT operations keep their existing API.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'pysat'

    def __init__(self, source_model: FeatureModel, cnf_method: str = 'distributive') -> None:
        self.source_model = source_model
        # 'distributive' (default) or 'tseytin'; forwarded to the shared CNF encoder.
        self.cnf_method = cnf_method
        self.destination_model = PySATModel()
        self.destination_model.original_model = source_model

    def transform(self) -> PySATModel:
        clause_set = ClauseSet.from_feature_model(self.source_model, cnf_method=self.cnf_method)
        model = self.destination_model
        for clause in clause_set.clauses:
            model.add_clause(clause)
        model.variables = dict(clause_set.variables)
        model.features = dict(clause_set.features)
        model.auxiliary_variables = set(clause_set.auxiliary_variables)
        return model
