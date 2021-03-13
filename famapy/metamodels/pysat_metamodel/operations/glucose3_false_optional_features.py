from famapy.core.operations import FalseOptionalFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_core_features import Glucose3CoreFeatures


class Glucose3FalseOptionalFeatures(FalseOptionalFeatures):

    def __init__(self):
        self.false_optional_features = []
        self.core_features = None

    def get_false_optional_features(self):
        return self.false_optional_features

    def get_result(self):
        return self.get_false_optional_features()

    def set_core_features(self, core_features: list):
        self.core_features = core_features

    def set_up(self, pysat_model: PySATModel, have_core):
        if not have_core:
            core_features = Glucose3CoreFeatures()
            core_features.execute(pysat_model)
            core_features = core_features.get_core_features()
            self.core_features=core_features

    def execute(self, pysat_model: PySATModel, fm_model: FeatureModel) -> 'Glucose3FalseOptionalFeatures':
        self.set_up(pysat_model, self.core_features is not None)

        false_optional = []
        for feat in self.core_features:
            for relation in fm_model.relations:
                children_names = [feat.name for feat in relation.children]
                if relation.is_optional() and feat in children_names:
                    false_optional.append(feat)
                    break

        self.false_optional_features=false_optional
        return self
