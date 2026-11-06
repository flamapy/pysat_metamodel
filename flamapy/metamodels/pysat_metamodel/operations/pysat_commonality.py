from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.exceptions import FlamaException
from flamapy.core.operations import Commonality
from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

MAX_SHOWN = 10  # unknown features listed in the error message


class PySATCommonality(Commonality):
    """The commonality of a (partial) configuration, by enumerating the products of the model
    (the descriptor is the ``Commonality`` interface's)."""

    def __init__(self) -> None:
        self.result: float = 0
        self.configuration = Configuration({})

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def get_commonality(self) -> float:
        return self.get_result()

    def get_result(self) -> float:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATCommonality':
        self.result = commonality(cast(PySATModel, model), self.configuration)
        return self


def configuration_literals(model: PySATModel, configuration: Configuration) -> list[int]:
    """The literals a product must satisfy to include the configuration: the variable of every
    selected feature and the negated variable of every deselected one (every feature not in a
    full configuration counts as deselected). Unknown features are an error."""
    unknown = [str(feature) for feature in configuration.elements if feature not in model.variables]
    if unknown:
        raise FlamaException(f'The configuration contains features that are not in the model: '
                             f'{", ".join(unknown[:MAX_SHOWN])}'
                             f'{", ..." if len(unknown) > MAX_SHOWN else ""}')
    decided: dict[Any, bool] = {feature: configuration.is_selected(feature)
                                for feature in configuration.elements}
    if configuration.is_full:
        for feature in model.variables:
            decided.setdefault(feature, False)
    return [model.variables[feature] if selected else -model.variables[feature]
            for feature, selected in decided.items()]


def commonality(model: PySATModel, configuration: Configuration) -> float:
    """The fraction of the products of the model that include the configuration (0 when the
    model is void). The products are enumerated once, over the features."""
    literals = set(configuration_literals(model, configuration))
    total = included = 0
    solver = Solver(name='glucose3', bootstrap_with=model.get_all_clauses().clauses)
    try:
        for product in model.enum_feature_models(solver):
            total += 1
            if literals <= set(product):
                included += 1
    finally:
        solver.delete()
    return included / total if total else 0.0
