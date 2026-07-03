from typing import Tuple

from flamapy.metamodels.pysat_diagnosis_metamodel.models import DiagnosisModel
from flamapy.core.operations.descriptor import OperationDescriptor, Input
from . import PySATAbstractIdentifier
from .diagnosis.checker import ConsistencyChecker
from .diagnosis.hsdag.hsdag import HSDAG
from .diagnosis.hsdag.labeler.quickxplain_labeler import QuickXPlainParameters, QuickXPlainLabeler


class PySATConflict(PySATAbstractIdentifier):
    """
    An operation that computes conflicts and diagnoses
    using the combination of HSDAG and QuickXPlain algorithms.
    Four optional inputs:
    - configuration - a configuration to be diagnosed
    - test_case - a test case to be used for diagnosis
    - max_conflicts - specify the maximum number of conflicts to be computed
    - max_depth - specify the maximum depth of the HSDAG to be computed
    """

    facade = OperationDescriptor(
        doc=(
            'Returns a list of conflict sets: minimal subsets of the model constraints that\n'
            'are inconsistent with the given configuration. Requires the pysat_diagnosis\n'
            'plugin.\n'
            '\n'
            '``configuration_path`` accepts a configuration file path, a ``{feature:\n'
            'value}`` mapping, or a Configuration object. ``test_case_path`` is optional\n'
            'and, when given, looks for conflicts against that expected outcome instead;\n'
            'same input types.'
        ),
        returns='Union[None, List[str]]',
        name='conflict', operation='PySATConflict', default_backend='pysat_diagnosis',
        inputs=(
            Input('configuration_path', str, required=True, kind='configuration',
                  setter='set_configuration'),
            Input('test_case_path', str, default=None, kind='configuration',
                  setter='set_test_case'),
            Input('max_conflicts', int, default=None, setter='set_max_conflicts'),
        ),
    )

    def __init__(self) -> None:
        super().__init__()
        self.max_conflicts = -1  # -1 means no limit

    def set_max_conflicts(self, max_conflicts: int) -> None:
        self.max_conflicts = max_conflicts

    def prepare_hsdag(self, model: DiagnosisModel) -> Tuple[ConsistencyChecker, HSDAG]:
        # transform model to diagnosis model
        model.prepare_diagnosis_task(configuration=self.configuration, test_case=self.test_case)
        # print(f'C: {diag_model.get_C()}')
        # print(f'B: {diag_model.get_B()}')

        set_c = model.get_c()

        # if self.configuration is None:
        # reverse the list to get the correct order of constraints in the diagnosis messages
        #     C.reverse()

        checker = ConsistencyChecker(self.solver_name, model.get_kb())
        parameters = QuickXPlainParameters(set_c, [], model.get_b())
        labeler = QuickXPlainLabeler(checker, parameters)

        hsdag = HSDAG(labeler)
        hsdag.max_number_conflicts = self.max_conflicts
        hsdag.max_depth = self.max_depth

        return checker, hsdag

    def set_result_messages(self, cs_mess: str, diag_mess: str) -> None:
        self.result_messages.append(cs_mess)
        self.result_messages.append(diag_mess)
