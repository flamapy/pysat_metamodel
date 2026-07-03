"""Diagnosis-powered operations for interactive configuration.

These turn the low-level QuickXPlain/FastDiag machinery into configuration-level answers
that a configurator can surface directly:

- ``PySATConfigurationConflict``: a minimal set of user decisions that together with the
  model are inconsistent ("these choices clash").
- ``PySATConfigurationRepair``: a minimal set of decisions to retract to restore
  consistency ("undo one of these to continue").
- ``PySATFeatureExplanation``: for a feature that is forced by the current decisions, the
  minimal set of decisions responsible ("this feature is on because of these choices").

Each consumes a ``PySATModel`` (the feature-model CNF) and a partial ``Configuration``.
Decisions are returned as ``(feature_name, selected)`` pairs.
"""
from typing import Optional, cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

from .diagnosis.checker import ConsistencyChecker
from .diagnosis.quickxplain import QuickXPlain
from .diagnosis.fastdiag import FastDiag


Decision = tuple[str, bool]


def _clauses_and_decisions(
    model: PySATModel, configuration: Configuration
) -> tuple[list[list[int]], list[tuple[int, str, bool]]]:
    clauses = [list(clause) for clause in model.get_all_clauses().clauses]
    decisions: list[tuple[int, str, bool]] = []
    for name, value in configuration.elements.items():
        variable = model.variables.get(name)
        if variable is None:
            continue
        selected = bool(value)
        decisions.append((variable if selected else -variable, name, selected))
    return clauses, decisions


def _decisions_from_literals(
    literals: list[int], decisions: list[tuple[int, str, bool]]
) -> list[Decision]:
    by_literal = {literal: (name, value) for literal, name, value in decisions}
    return [by_literal[literal] for literal in literals if literal in by_literal]


class PySATConfigurationConflict(Operation):
    """Minimal subset of the user's decisions that is inconsistent with the model."""

    facade = OperationDescriptor(
        doc=(
            'Returns a minimal subset of the configuration decisions that is inconsistent with\n'
            'the feature model — the conflict explaining why the (partial) configuration cannot\n'
            'be completed. Requires the pysat_diagnosis plugin.'
        ),
        returns='Union[None, List[Any]]',
        name='configuration_conflict', operation='PySATConfigurationConflict',
        default_backend='pysat_diagnosis',
        inputs=(Input('configuration_path', str, required=True, kind='configuration',
                      setter='set_configuration'),),
    )

    def __init__(self) -> None:
        self._configuration: Optional[Configuration] = None
        self._result: list[Decision] = []

    def set_configuration(self, configuration: Configuration) -> None:
        self._configuration = configuration

    def get_conflict(self) -> list[Decision]:
        return self._result

    def get_result(self) -> list[Decision]:
        return self._result

    def execute(self, model: VariabilityModel) -> 'PySATConfigurationConflict':
        sat_model = cast(PySATModel, model)
        clauses, decisions = _clauses_and_decisions(sat_model, self._configuration)
        checker = ConsistencyChecker('glucose3', clauses)
        conflict = QuickXPlain(checker).find_conflict([lit for lit, _, _ in decisions], [])
        checker.delete()
        self._result = _decisions_from_literals(conflict, decisions)
        return self


class PySATConfigurationRepair(Operation):
    """Minimal subset of the user's decisions to retract to restore consistency."""

    facade = OperationDescriptor(
        doc=(
            'Returns a minimal subset of the configuration decisions to retract in order to\n'
            'restore consistency with the feature model — how to repair an over-constrained\n'
            'configuration. Requires the pysat_diagnosis plugin.'
        ),
        returns='Union[None, List[Any]]',
        name='configuration_repair', operation='PySATConfigurationRepair',
        default_backend='pysat_diagnosis',
        inputs=(Input('configuration_path', str, required=True, kind='configuration',
                      setter='set_configuration'),),
    )

    def __init__(self) -> None:
        self._configuration: Optional[Configuration] = None
        self._result: list[Decision] = []

    def set_configuration(self, configuration: Configuration) -> None:
        self._configuration = configuration

    def get_repair(self) -> list[Decision]:
        return self._result

    def get_result(self) -> list[Decision]:
        return self._result

    def execute(self, model: VariabilityModel) -> 'PySATConfigurationRepair':
        sat_model = cast(PySATModel, model)
        clauses, decisions = _clauses_and_decisions(sat_model, self._configuration)
        checker = ConsistencyChecker('glucose3', clauses)
        diagnosis = FastDiag(checker).find_diagnosis([lit for lit, _, _ in decisions], [])
        checker.delete()
        self._result = _decisions_from_literals(diagnosis, decisions)
        return self


class PySATFeatureExplanation(Operation):
    """Explain why a feature is forced by the current decisions.

    ``get_forced_value()`` is the value the feature is forced to (or ``None`` if it is not
    forced), and ``get_result()`` is the minimal set of decisions responsible.
    """

    facade = OperationDescriptor(
        doc=(
            'Explains why a feature is forced (selected or deselected) by the current\n'
            'configuration: returns the minimal set of decisions responsible. ``feature_name``\n'
            'is the feature to explain. Requires the pysat_diagnosis plugin.'
        ),
        returns='Union[None, List[Any]]',
        name='feature_explanation', operation='PySATFeatureExplanation',
        default_backend='pysat_diagnosis',
        inputs=(
            Input('configuration_path', str, required=True, kind='configuration',
                  setter='set_configuration'),
            Input('feature_name', str, required=True, setter='set_feature'),
        ),
    )

    def __init__(self) -> None:
        self._configuration: Optional[Configuration] = None
        self._feature: Optional[str] = None
        self._forced_value: Optional[bool] = None
        self._result: list[Decision] = []

    def set_configuration(self, configuration: Configuration) -> None:
        self._configuration = configuration

    def set_feature(self, feature_name: str) -> None:
        self._feature = feature_name

    def get_forced_value(self) -> Optional[bool]:
        return self._forced_value

    def get_explanation(self) -> list[Decision]:
        return self._result

    def get_result(self) -> list[Decision]:
        return self._result

    def execute(self, model: VariabilityModel) -> 'PySATFeatureExplanation':
        sat_model = cast(PySATModel, model)
        self._forced_value = None
        self._result = []
        if self._feature is None:
            return self
        clauses, decisions = _clauses_and_decisions(sat_model, self._configuration)
        variable = sat_model.variables.get(self._feature)
        if variable is None:
            return self

        literals = [lit for lit, _, _ in decisions]
        checker = ConsistencyChecker('glucose3', clauses)
        can_be_true = checker.is_consistent([*literals, variable], [])
        can_be_false = checker.is_consistent([*literals, -variable], [])
        if can_be_true and not can_be_false:
            self._forced_value = True
            forbidden = -variable
        elif can_be_false and not can_be_true:
            self._forced_value = False
            forbidden = variable
        else:
            checker.delete()  # not forced (or already contradictory) -> no explanation
            return self

        # The minimal decisions that, with the model, entail the forced value are those
        # inconsistent with the model plus the opposite assignment.
        explanation = QuickXPlain(checker).find_conflict(literals, [forbidden])
        checker.delete()
        self._result = _decisions_from_literals(explanation, decisions)
        return self
