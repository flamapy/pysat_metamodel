from typing import Any

from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models import Configuration

from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.diagnosis_model import DiagnosisModel
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.quickxplain import QuickXPlain
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.checker import ConsistencyChecker


class Glucose3QuickXPlain(Operation):

    def __init__(self) -> None:
        self.result = False
        self.configuration = None
        self.test_case = None
        self.solverName = 'glucose3'
        self.diagnosis_messages: list[str] = []

        self.checker = None

    def get_diagnosis_messages(self) -> list[Any]:
        return self.get_result()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def set_test_case(self, test_case: Configuration) -> None:
        self.test_case = test_case

    def get_result(self) -> list[str]:
        return self.diagnosis_messages

    def execute(self, model: PySATModel) -> 'Glucose3QuickXPlain':
        # transform model to diagnosis model
        diag_model = DiagnosisModel(model)
        diag_model.prepare_diagnosis_task(configuration=self.configuration, test_case=self.test_case)

        print(f'C: {diag_model.get_C()}')
        print(f'B: {diag_model.get_B()}')

        checker = ConsistencyChecker(self.solverName, diag_model.get_KB())
        quickxplain = QuickXPlain(checker)

        cs = quickxplain.findConflictSet(diag_model.get_C(), diag_model.get_B())

        if cs:
            mess = f'Conflicts: ['
            mess += diag_model.get_diagnosis(cs)
            mess += ']'
            self.diagnosis_messages.append(mess)

        checker.delete()

        return self
