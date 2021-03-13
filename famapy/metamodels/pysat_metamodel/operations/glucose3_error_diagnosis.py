from famapy.core.operations import ErrorDiagnosis
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_dead_features import Glucose3DeadFeatures
from famapy.metamodels.pysat_metamodel.operations.glucose3_false_optional_features import Glucose3FalseOptionalFeatures


class Glucose3ErrorDiagnosis(ErrorDiagnosis):

    def __init__(self):
        self.diagnosis_messages = []
        self.dead_features = None
        self.false_optional_features = None

    def get_diagnosis_messages(self):
        return self.diagnosis_messages

    def get_result(self):
        return self.get_diagnosis_messages()

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

    def execute(self, pysat_model: PySATModel, fm_model: FeatureModel) -> 'Glucose3ErrorDiagnosis':
        self.set_up(pysat_model, fm_model, self.dead_features is not None, self.false_optional_features is not None)

        if self.dead_features:
            for feat in fm_model.get_features():
                if feat.name in self.dead_features:
                    for ctc in fm_model.get_constraints():
                        if feat.name == ctc.destination.name and ctc.ctc_type == 'excludes':
                            self.diagnosis_messages.append("Delete the feature " + feat.name +
                                " and the constraint: " + ctc.origin.name + " " + ctc.ctc_type +
                                " " + ctc.destination.name + ", or simply delete the constraint")

        if self.false_optional_features:
            for feat in fm_model.get_features():
                if feat.name in self.false_optional_features:
                    for ctc in fm_model.get_constraints():
                        if feat.name == ctc.destination.name and ctc.ctc_type == 'requires':
                            self.diagnosis_messages.append("Convert the feature " + feat.name +
                                " to mandatory and delete the constraint: " + ctc.origin.name +
                                " " + ctc.ctc_type + " " +ctc.destination.name)

        return self
