from typing import Any

from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models import Configuration

from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.diagnosis_model import DiagnosisModel
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.hsdag.hsdag import HSDAG
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.hsdag.labeler.quickxplain_labeler import \
    QuickXPlainParameters, QuickXPlainLabeler
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.checker import ConsistencyChecker


class Glucose3Conflict(Operation):
    """
    An operation that computes conflicts and diagnoses using the combination of HSDAG and QuickXPlain algorithms.
    Four optional inputs:
    - configuration - a configuration to be diagnosed
    - test_case - a test case to be used for diagnosis
    - max_conflicts - specify the maximum number of conflicts to be computed
    - max_depth - specify the maximum depth of the HSDAG to be computed
    """

    def __init__(self) -> None:
        self.result = False
        self.configuration = None
        self.test_case = None
        self.solverName = 'glucose3'
        self.diagnosis_messages: list[str] = []

        self.checker = None
        self.max_conflicts = -1  # -1 means no limit
        self.max_depth = 0  # 0 means no limit

    def set_max_conflicts(self, max_conflicts: int) -> None:
        self.max_conflicts = max_conflicts

    def set_max_depth(self, max_depth: int) -> None:
        self.max_depth = max_depth

    def get_diagnosis_messages(self) -> list[Any]:
        return self.get_result()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def set_test_case(self, test_case: Configuration) -> None:
        self.test_case = test_case

    def get_result(self) -> list[str]:
        return self.diagnosis_messages

    def execute(self, model: PySATModel) -> 'Glucose3Conflict':
        # transform model to diagnosis model
        diag_model = DiagnosisModel(model)
        diag_model.prepare_diagnosis_task(configuration=self.configuration, test_case=self.test_case)

        # print(f'C: {diag_model.get_C()}')
        # print(f'B: {diag_model.get_B()}')

        C = diag_model.get_C()
        # if self.configuration is None:
        #     C.reverse()  # reverse the list to get the correct order of constraints in the diagnosis messages

        checker = ConsistencyChecker(self.solverName, diag_model.get_KB())
        parameters = QuickXPlainParameters(C, [], diag_model.get_B())
        quickxplain = QuickXPlainLabeler(checker, parameters)
        hsdag = HSDAG(quickxplain)
        hsdag.max_number_conflicts = self.max_conflicts
        hsdag.max_depth = self.max_depth

        hsdag.construct()

        diagnoses = hsdag.get_diagnoses()
        conflicts = hsdag.get_conflicts()

        if len(diagnoses) == 0:
            diag_mess = 'No diagnosis found'
        elif len(diagnoses) == 1:
            diag_mess = f'Diagnosis: '
            diag_mess += diag_model.get_pretty_diagnoses(diagnoses)
        else:
            diag_mess = f'Diagnoses: '
            diag_mess += diag_model.get_pretty_diagnoses(diagnoses)

        if len(conflicts) == 0:
            cs_mess = 'No conflicts found'
        elif len(conflicts) == 1:
            cs_mess = f'Conflict: '
            cs_mess += diag_model.get_pretty_diagnoses(conflicts)
        else:
            cs_mess = f'Conflicts: '
            cs_mess += diag_model.get_pretty_diagnoses(conflicts)

        self.diagnosis_messages.append(cs_mess)
        self.diagnosis_messages.append(diag_mess)
        checker.delete()
        return self
