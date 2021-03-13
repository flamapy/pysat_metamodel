from famapy.core.operations import ErrorDetection
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_dead_features import Glucose3DeadFeatures
from famapy.metamodels.pysat_metamodel.operations.glucose3_false_optional_features import Glucose3FalseOptionalFeatures


class Glucose3ErrorDetection(ErrorDetection):

    def __init__(self):
        self.errors_messages = []
        self.dead_features = None
        self.false_optional_features = None

    def get_errors_messages(self):
        return self.errors_messages

    def get_result(self):
        return self.get_errors_messages()

    def set_dead_features(self, dead_features: list):
        self.dead_features = dead_features

    def set_false_optional_features(self, false_optional_features: list):
        self.false_optional_features = false_optional_features

    def set_up(self, pysat_model: PySATModel, fm_model: FeatureModel, have_dead, have_false_optionals):
        if not have_dead:
            dead_features = Glucose3DeadFeatures()
            dead_features.execute(pysat_model)
            dead_features = dead_features.get_dead_features()
            self.dead_features=dead_features
        if not have_false_optionals:
            false_optional_features = Glucose3FalseOptionalFeatures()
            false_optional_features.execute(pysat_model,fm_model)
            false_optional_features = false_optional_features.get_false_optional_features()
            self.false_optional_features=false_optional_features

    def execute(self, pysat_model: PySATModel, fm_model: FeatureModel) -> 'Glucose3ErrorDetection':
        self.set_up(pysat_model, fm_model, self.dead_features is not None, self.false_optional_features is not None)

        if self.dead_features:
            self.errors_messages.append("The model have " + str(self.dead_features) + " dead features")
        else:
            self.errors_messages.append("The model haven't dead features")

        if self.false_optional_features:
            self.errors_messages.append("The model have " + str(self.false_optional_features) + " false optionals features")
        else:
            self.errors_messages.append("The model haven't false optionals features")

        return self
