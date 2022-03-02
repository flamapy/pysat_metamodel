#from pysat.solvers import Glucose3

from famapy.core.operations import ErrorDetection
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_dead_features import (
    Glucose3DeadFeatures
)
from famapy.metamodels.pysat_metamodel.operations.glucose3_false_optional_features import (
    Glucose3FalseOptionalFeatures
)
from famapy.metamodels.pysat_metamodel.operations.glucose3_valid import Glucose3Valid
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel


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

        # Redundancies
        # TODO: reimplement in another way.
        #     redundancies = []
        #     for feat in model.features:
        #         if not glucose_r.solve(assumptions=[-feat]):
        #             for clause in model.ctc_cnf:
        #                 if clause[1] == feat:
        #                     if clause[0] < 0:
        #                         redundancies.append(
        #                             model.features.get(-clause[0]) +
        #                             ' requires ' +
        #                             model.features.get(feat)
        #                         )
        #                 if clause[0] == feat:
        #                     if clause[1] < 0:
        #                         redundancies.append(
        #                             model.features.get(feat) +
        #                             ' requires ' +
        #                             model.features.get(-clause[1])
        #                         )

        #     variables = []
        #     for clause in model.ctc_cnf:
        #         if clause[1] in variables:
        #             if clause[1] > 0:
        #                 redundancies.append(
        #                     model.features.get(abs(clause[0])) +
        #                     ' requires ' +
        #                     model.features.get(abs(clause[1]))
        #                 )
        #             else:
        #                 redundancies.append(
        #                     model.features.get(abs(clause[0])) +
        #                     ' excludes ' +
        #                     model.features.get(abs(clause[1]))
        #                 )
        #         variables.append(clause[1])

        #     if redundancies:
        #         self.errors_messages.append(
        #             'Redundancies: ' + str(redundancies))
        # else:
        #     self.errors_messages.append(
        #         'The model is void, so have not any product')
