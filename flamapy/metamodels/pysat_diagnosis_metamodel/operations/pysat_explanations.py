"""User-facing explanation operations: minimal conflicts in constraint names, not indices.

Both operations compute a QuickXPlain minimal conflict over the model's relationships and
cross-tree constraints and report it through the :class:`Explanation` value type, whose
items carry the encoder's human-readable descriptions.

They rebuild a pristine diagnosis model from ``original_model`` on every execution:
``prepare_diagnosis_task`` mutates the encoded clauses in place, so reusing the (facade-
cached) model across calls with different inputs would corrupt the assumption ids.
"""
from typing import Optional, cast

from flamapy.core.exceptions import FlamaException
from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input
from flamapy.core.reasoning import QuickXPlain
from flamapy.core.reasoning.hsdag import HSDAG
from flamapy.core.reasoning.hsdag.labeler.fastdiag_labeler import (
    FastDiagLabeler,
    FastDiagParameters,
)
from flamapy.metamodels.configuration_metamodel.models import Configuration

from ..models.explanation import Explanation, ExplanationItem
from ..models.pysat_diagnosis_model import DiagnosisModel
from ..transformations.fm_to_diag_pysat import FmToDiagPysat
from .diagnosis.checker import ConsistencyChecker


def _explanation_descriptions(explanation: Explanation) -> list[str]:
    return explanation.descriptions()


def _corrections_descriptions(explanations: list[Explanation]) -> list[list[str]]:
    return [explanation.descriptions() for explanation in explanations]


def _prepared_model(
    model: DiagnosisModel, test_case: Optional[Configuration]
) -> DiagnosisModel:
    """A pristine diagnosis model with the task prepared.

    ``prepare_diagnosis_task`` mutates the encoded clauses in place, so the (facade-cached)
    input model is never prepared directly: we re-encode from ``original_model``.
    """
    original = getattr(model, 'original_model', None)
    working = FmToDiagPysat(original).transform() if original is not None else model
    working.prepare_diagnosis_task(test_case=test_case)
    return working


def _explanation_from(working: DiagnosisModel, indices: list[int]) -> Explanation:
    original = getattr(working, 'original_model', None)
    constraint_reprs = (
        {str(ctc) for ctc in original.get_constraints()} if original is not None else set())
    return Explanation(tuple(
        ExplanationItem(
            constraint_repr=working.constraint_assumption_map[index],
            index=index,
            kind='constraint'
            if working.constraint_assumption_map[index] in constraint_reprs
            else 'relationship',
        )
        for index in sorted(indices)))


def _minimal_conflict(
    model: DiagnosisModel, test_case: Optional[Configuration], solver_name: str
) -> Explanation:
    working = _prepared_model(model, test_case)
    checker = ConsistencyChecker(solver_name, working.get_kb())
    try:
        conflict = QuickXPlain(checker).find_conflict(working.get_c(), working.get_b())
    finally:
        checker.delete()
    return _explanation_from(working, conflict)


class PySATExplainVoidModel(Operation):
    """Why is the model void? A minimal, human-readable conflict among its constraints."""

    facade = OperationDescriptor(
        doc=(
            'Explains why the feature model is void (encodes no valid configuration): a\n'
            'minimal set of relationships/cross-tree constraints that is already\n'
            'unsatisfiable (a QuickXPlain minimal conflict), in human-readable form.\n'
            'Returns an empty list when the model is satisfiable. Requires the\n'
            'pysat_diagnosis plugin.'
        ),
        returns='Union[None, List[str]]',
        name='explain_void_model', operation='PySATExplainVoidModel',
        default_backend='pysat_diagnosis',
        result_adapter=_explanation_descriptions,
    )

    def __init__(self) -> None:
        self.result = Explanation()
        self.solver_name = 'glucose3'

    def execute(self, model: VariabilityModel) -> 'PySATExplainVoidModel':
        self.result = _minimal_conflict(cast(DiagnosisModel, model), None, self.solver_name)
        return self

    def get_result(self) -> Explanation:
        return self.result

    def get_explanation(self) -> Explanation:
        return self.result


class PySATExplainFalseOptional(Operation):
    """Why is this feature false-optional? Conflict of the model plus parent without child."""

    facade = OperationDescriptor(
        doc=(
            'Explains why a feature is false-optional (declared optional but present in\n'
            'every valid configuration that includes its parent): a minimal set of\n'
            'relationships/cross-tree constraints that forbids deselecting it while its\n'
            'parent is selected (a QuickXPlain minimal conflict of the model plus\n'
            '"parent = true, feature = false"), in human-readable form. Returns an empty\n'
            'list when the feature is not false-optional. Requires the pysat_diagnosis\n'
            'plugin.'
        ),
        returns='Union[None, List[str]]',
        name='explain_false_optional', operation='PySATExplainFalseOptional',
        default_backend='pysat_diagnosis',
        inputs=(Input('feature_name', str, required=True, setter='set_feature'),),
        result_adapter=_explanation_descriptions,
    )

    def __init__(self) -> None:
        self.feature = ''
        self.result = Explanation()
        self.solver_name = 'glucose3'

    def set_feature(self, feature_name: str) -> None:
        self.feature = feature_name

    def execute(self, model: VariabilityModel) -> 'PySATExplainFalseOptional':
        diag_model = cast(DiagnosisModel, model)
        original = getattr(diag_model, 'original_model', None)
        feature = (original.get_feature_by_name(self.feature)
                   if original is not None else None)
        if feature is None:
            raise FlamaException(f"Feature '{self.feature}' is not in the model.")
        parent = feature.get_parent()
        if parent is None:
            raise FlamaException(
                f"Feature '{self.feature}' is the root; it cannot be false-optional.")
        test_case = Configuration({parent.name: True, self.feature: False})
        try:
            self.result = _minimal_conflict(diag_model, test_case, self.solver_name)
        except KeyError as error:
            raise FlamaException(
                f"Feature '{self.feature}' is not in the model.") from error
        return self

    def get_result(self) -> Explanation:
        return self.result

    def get_explanation(self) -> Explanation:
        return self.result


class PySATMinimalCorrections(Operation):
    """Minimal constraint sets whose removal makes a void model satisfiable (FastDiag)."""

    facade = OperationDescriptor(
        doc=(
            'Returns the minimal corrections for a void feature model: each correction is\n'
            'a minimal set of relationships/cross-tree constraints whose removal makes\n'
            'the model satisfiable (FastDiag diagnoses enumerated via HSDAG), in\n'
            'human-readable form. Returns an empty list when the model is already\n'
            'satisfiable. ``max_corrections`` bounds how many are enumerated. Requires\n'
            'the pysat_diagnosis plugin.'
        ),
        returns='Union[None, List[List[str]]]',
        name='minimal_corrections', operation='PySATMinimalCorrections',
        default_backend='pysat_diagnosis',
        inputs=(Input('max_corrections', int, default=None, setter='set_max_corrections'),),
        result_adapter=_corrections_descriptions,
    )

    def __init__(self) -> None:
        self.max_corrections = -1  # -1 means no limit
        self.result: list[Explanation] = []
        self.solver_name = 'glucose3'

    def set_max_corrections(self, max_corrections: int) -> None:
        self.max_corrections = max_corrections

    def execute(self, model: VariabilityModel) -> 'PySATMinimalCorrections':
        working = _prepared_model(cast(DiagnosisModel, model), None)
        checker = ConsistencyChecker(self.solver_name, working.get_kb())
        try:
            parameters = FastDiagParameters(working.get_c(), [], working.get_b())
            hsdag = HSDAG(FastDiagLabeler(checker, parameters))
            hsdag.max_number_diagnoses = self.max_corrections
            hsdag.construct()
            diagnoses = hsdag.get_diagnoses()
        finally:
            checker.delete()
        self.result = [_explanation_from(working, diagnosis) for diagnosis in diagnoses]
        return self

    def get_result(self) -> list[Explanation]:
        return self.result

    def get_corrections(self) -> list[Explanation]:
        return self.result


class PySATExplainDeadFeature(Operation):
    """Why is this feature dead? A minimal conflict of the model plus 'feature = true'."""

    facade = OperationDescriptor(
        doc=(
            'Explains why a feature is dead (appears in no valid configuration): a\n'
            'minimal set of relationships/cross-tree constraints that forbids selecting\n'
            'it (a QuickXPlain minimal conflict of the model plus "feature = true"), in\n'
            'human-readable form. Returns an empty list when the feature is not dead.\n'
            'Requires the pysat_diagnosis plugin.'
        ),
        returns='Union[None, List[str]]',
        name='explain_dead_feature', operation='PySATExplainDeadFeature',
        default_backend='pysat_diagnosis',
        inputs=(Input('feature_name', str, required=True, setter='set_feature'),),
        result_adapter=_explanation_descriptions,
    )

    def __init__(self) -> None:
        self.feature = ''
        self.result = Explanation()
        self.solver_name = 'glucose3'

    def set_feature(self, feature_name: str) -> None:
        self.feature = feature_name

    def execute(self, model: VariabilityModel) -> 'PySATExplainDeadFeature':
        diag_model = cast(DiagnosisModel, model)
        test_case = Configuration({self.feature: True})
        try:
            self.result = _minimal_conflict(diag_model, test_case, self.solver_name)
        except KeyError as error:
            raise FlamaException(
                f"Feature '{self.feature}' is not in the model.") from error
        return self

    def get_result(self) -> Explanation:
        return self.result

    def get_explanation(self) -> Explanation:
        return self.result
