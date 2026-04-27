from typing import Any, cast


from flamapy.core.operations import DeadFeatures
from flamapy.metamodels.pysat_metamodel.operations import PySATBackbone
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATDeadFeatures(DeadFeatures):

    def __init__(self) -> None:
        self.dead_features: list[Any] = []

    def get_dead_features(self) -> list[Any]:
        return self.dead_features

    def get_result(self) -> list[Any]:
        return self.get_dead_features()

    def execute(self, model: VariabilityModel) -> 'PySATDeadFeatures':
        sat_model = cast(PySATModel, model)
        self.dead_features = PySATBackbone().execute(sat_model).get_result()["dead"]
        return self
