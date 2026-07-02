from typing import Any, Optional, cast

from pysat.formula import WCNF
from pysat.examples.rc2 import RC2

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import AttributeOptimization, OptimizationGoal
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class PySATAttributeOptimization(AttributeOptimization):
    """Optimal configuration for a single numeric feature attribute, via MaxSAT (RC2).

    The objective is the sum of the attribute value over the selected features. The SAT
    clauses are the hard constraints; per-feature attribute values become weighted soft
    clauses so RC2 returns a valid configuration with the optimal objective.

    Multi-objective/Pareto optimization is not supported here — use the z3 backend for that.
    """

    def __init__(self) -> None:
        self._attributes: dict[str, OptimizationGoal] = {}
        self._result: list[Configuration] = []
        self._optimum: dict[str, float] = {}

    def set_attributes(self, attributes: dict) -> None:
        self._attributes = attributes

    def optimize(self) -> list:
        return self.get_result()

    def get_result(self) -> list:
        return self._result

    def get_optimum(self) -> dict:
        """The optimal objective value per attribute, e.g. ``{'Cost': 12.0}``."""
        return self._optimum

    def execute(self, model: VariabilityModel) -> 'PySATAttributeOptimization':
        sat_model = cast(PySATModel, model)
        if len(self._attributes) != 1:
            raise FlamaException(
                'PySATAttributeOptimization optimizes a single attribute; use the z3 '
                'backend for multi-objective/Pareto optimization.'
            )
        (attr_name, goal), = self._attributes.items()
        feature_model = getattr(sat_model, 'original_model', None)
        if feature_model is None:
            raise FlamaException(
                'The SAT model has no attached feature model to read attributes from.'
            )
        weights = _feature_weights(cast(FeatureModel, feature_model), attr_name)
        config, optimum = _optimize(sat_model, weights, goal)
        self._result = [] if config is None else [config]
        self._optimum = {} if config is None else {attr_name: optimum}
        return self


def _feature_weights(feature_model: FeatureModel, attribute_name: str) -> dict[str, float]:
    """Map each feature carrying the given numeric attribute to its value."""
    weights: dict[str, float] = {}
    for feature in feature_model.get_features():
        for attribute in feature.get_attributes():
            value = attribute.default_value
            if attribute.name == attribute_name and isinstance(value, (int, float)) \
                    and not isinstance(value, bool):
                weights[feature.name] = float(value)
    return weights


def _integer_scale(values: list[float]) -> int:
    """Smallest power of ten that turns all values into integers (capped at 1e6)."""
    max_decimals = 0
    for value in values:
        text = f"{value:.6f}".rstrip('0')
        if '.' in text:
            max_decimals = max(max_decimals, len(text.split('.')[1]))
    return 10 ** max_decimals


def _optimize(sat_model: PySATModel,
              weights: dict[str, float],
              goal: OptimizationGoal) -> tuple[Optional[Configuration], Optional[float]]:
    # Maximizing an objective is minimizing its negation.
    sign = 1.0 if goal == OptimizationGoal.MINIMIZE else -1.0
    effective = {name: sign * weight for name, weight in weights.items()}
    scale = _integer_scale(list(effective.values()))

    wcnf = WCNF()
    for clause in sat_model.get_all_clauses():
        wcnf.append(list(clause))  # hard clauses

    for name, weight in effective.items():
        variable = sat_model.variables.get(name)
        if variable is None:
            continue
        int_weight = int(round(weight * scale))
        if int_weight > 0:
            # Cost paid when the feature is selected -> pushes it out to reduce the objective.
            wcnf.append([-variable], weight=int_weight)
        elif int_weight < 0:
            # Cost paid when the feature is deselected -> pulls it in.
            wcnf.append([variable], weight=-int_weight)

    with RC2(wcnf) as rc2:
        assignment = rc2.compute()
        if assignment is None:
            return None, None
        selected_vars = {literal for literal in assignment if literal > 0}
        elements: dict[Any, Any] = {}
        for literal in assignment:
            if literal > 0:
                feature_name = sat_model.features.get(literal)
                if feature_name is not None:  # skip auxiliary variables
                    elements[feature_name] = True
        configuration = Configuration(elements)

    optimum = sum(weight for name, weight in weights.items()
                  if sat_model.variables.get(name) in selected_vars)
    return configuration, optimum
