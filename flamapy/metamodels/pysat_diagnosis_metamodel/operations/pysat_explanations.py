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
from flamapy.metamodels.configuration_metamodel.models import Configuration

from ..models.explanation import Explanation, ExplanationItem
from ..models.pysat_diagnosis_model import DiagnosisModel
from ..transformations.fm_to_diag_pysat import FmToDiagPysat
from .diagnosis.checker import ConsistencyChecker
from .diagnosis.quickxplain import QuickXPlain


def _explanation_descriptions(explanation: Explanation) -> list[str]:
    return explanation.descriptions()


def _minimal_conflict(
    model: DiagnosisModel, test_case: Optional[Configuration], solver_name: str
) -> Explanation:
    original = getattr(model, 'original_model', None)
    working = FmToDiagPysat(original).transform() if original is not None else model
    working.prepare_diagnosis_task(test_case=test_case)
    checker = ConsistencyChecker(solver_name, working.get_kb())
    try:
        conflict = QuickXPlain(checker).find_conflict(working.get_c(), working.get_b())
    finally:
        checker.delete()

    constraint_reprs = (
        {str(ctc) for ctc in original.get_constraints()} if original is not None else set())
    items = tuple(
        ExplanationItem(
            constraint_repr=working.constraint_assumption_map[index],
            index=index,
            kind='constraint'
            if working.constraint_assumption_map[index] in constraint_reprs
            else 'relationship',
        )
        for index in sorted(conflict))
    return Explanation(items)


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
