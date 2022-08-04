#from pysat.solvers import Glucose3

from flamapy.core.operations import ErrorDetection
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.glucose3_dead_features import (
    Glucose3DeadFeatures
)
from flamapy.metamodels.pysat_metamodel.operations.glucose3_false_optional_features import (
    Glucose3FalseOptionalFeatures
)
from flamapy.metamodels.pysat_metamodel.operations.glucose3_valid import Glucose3Valid
from flamapy.metamodels.fm_metamodel.models.feature_model import FeatureModel


class Glucose3ErrorDetection(ErrorDetection):

    def __init__(self, feature_model: FeatureModel) -> None:
        self.feature_model = feature_model
        self.errors_messages: list[str] = []

    def get_errors_messages(self) -> list[str]:
        return self.get_result()

    def get_result(self) -> list[str]:
        return self.errors_messages

    def execute(self, model: PySATModel) -> 'Glucose3ErrorDetection':
        # Valid feature model check
        valid = Glucose3Valid().execute(model).get_result()
        if not valid:
            self.errors_messages.append('The model is not valid (it is void), \
                                        so it has not any product.')

        # Dead features detection
        dead_features = Glucose3DeadFeatures().execute(model).get_result()
        if dead_features:
            self.errors_messages.append(f'Dead features: {dead_features}')

        # False optional detection
        fof_op = Glucose3FalseOptionalFeatures(self.feature_model) 
        false_optional_features = fof_op.execute(model).get_result()
        if false_optional_features:
            self.errors_messages.append(f'False optional features: {false_optional_features}')

        return self
