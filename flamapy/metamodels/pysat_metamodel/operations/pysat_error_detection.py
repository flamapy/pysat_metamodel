from typing import Optional, cast

from flamapy.core.operations import ErrorDetection
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.pysat_dead_features import (
    PySATDeadFeatures
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_false_optional_features import (
    PySATFalseOptionalFeatures
)
from flamapy.core.models import VariabilityModel
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from flamapy.metamodels.pysat_metamodel.operations.pysat_valid import PySATValid


class PySATErrorDetection(ErrorDetection):

    def __init__(self) -> None:
        self.feature_model: Optional[FeatureModel] = None
        self.errors_messages: list[str] = []

    def get_errors_messages(self) -> list[str]:
        return self.get_result()

    def get_result(self) -> list[str]:
        return self.errors_messages

    def execute(self, model: VariabilityModel) -> 'PySATErrorDetection':
        if self.feature_model is None:
            raise FlamaException('The feature model is not setted')

        cast_model = cast(PySATModel, model)

        # Valid feature model check
        valid = PySATValid().execute(cast_model).get_result()
        if not valid:
            self.errors_messages.append('The model is not valid (it is void), \
                                        so it has not any product.')

        # Dead features detection
        dead_features = PySATDeadFeatures().execute(cast_model).get_result()
        if dead_features:
            self.errors_messages.append(f'Dead features: {dead_features}')

        # False optional detection
        fof_op = PySATFalseOptionalFeatures()
        fof_op.feature_model = self.feature_model
        false_optional_features = fof_op.execute(cast_model).get_result()
        if false_optional_features:
            self.errors_messages.append(f'False optional features: {false_optional_features}')

        return self
