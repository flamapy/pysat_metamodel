from typing import Any, cast


from flamapy.core.operations import CoreFeatures
from flamapy.metamodels.pysat_metamodel.operations import PySATBackbone
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATCoreFeatures(CoreFeatures):

    def __init__(self) -> None:
        self.core_features: list[Any] = []

    def get_core_features(self) -> list[Any]:
        return self.core_features

    def get_result(self) -> list[Any]:
        return self.get_core_features()

    def execute(self, model: VariabilityModel) -> 'PySATCoreFeatures':
        sat_model = cast(PySATModel, model)
        self.core_features = PySATBackbone().execute(sat_model).get_result()["core"]
        return self
