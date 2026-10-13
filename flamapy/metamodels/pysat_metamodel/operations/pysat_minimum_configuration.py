from typing import Any, Optional, cast

from pysat.formula import WCNF
from pysat.examples.rc2 import RC2

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class PySATMinimumConfiguration(Operation):
    """Return a valid configuration with the fewest selected features, via MaxSAT (RC2).

    Every feature contributes a unit soft clause preferring it to be deselected, so the
    optimum is a valid configuration minimizing the number of selected features (the
    minimum working configuration).
    """

    facade = OperationDescriptor(
        doc=(
            'Returns a valid configuration with the fewest selected features (the minimum\n'
            'working configuration).\n'
            '\n'
            '``backend`` selects the analysis plugin; only "sat" implements this operation.'
        ),
        returns='Union[None, Configuration]',
        name='minimum_configuration', operation='PySATMinimumConfiguration',
        default_backend='sat', selectable_backend=True,
    )

    def __init__(self) -> None:
        self._result: Optional[Configuration] = None
        self.partial_configuration: Configuration = None

    def set_partial_configuration(self, partial_configuration: Optional[Configuration]) -> None:
        self.partial_configuration = partial_configuration

    def get_result(self) -> Optional[Configuration]:
        return self._result

    def get_minimum_configuration(self) -> Optional[Configuration]:
        return self._result

    def execute(self, model: VariabilityModel) -> 'PySATMinimumConfiguration':
        sat_model = cast(PySATModel, model)
        wcnf = WCNF()
        for clause in sat_model.get_all_clauses():
            wcnf.append(list(clause))  # hard clauses
        
        # Partial configuration: each decision becomes a hard unit clause
        if self.partial_configuration is not None:
            for literal in _partial_configuration_assumptions(sat_model, self.partial_configuration):
                wcnf.append([literal])

        for variable in sat_model.features:  # one unit soft clause per feature variable
            wcnf.append([-variable], weight=1)

        with RC2(wcnf) as rc2:
            assignment = rc2.compute()
            if assignment is None:
                self._result = None
                return self
            elements: dict[Any, Any] = {}
            for literal in assignment:
                if literal > 0:
                    feature_name = sat_model.features.get(literal)
                    if feature_name is not None:  # skip auxiliary variables
                        elements[feature_name] = True
            self._result = Configuration(elements)
        return self


def _partial_configuration_assumptions(
    model: PySATModel, partial_configuration: Optional[Configuration]
) -> list[int]:
    """Literals fixing the features decided in a partial configuration."""
    literals: list[int] = []
    if partial_configuration is not None:
        for name, value in partial_configuration.elements.items():
            variable = model.variables.get(name)
            if variable is not None:
                literals.append(variable if value else -variable)
    return literals