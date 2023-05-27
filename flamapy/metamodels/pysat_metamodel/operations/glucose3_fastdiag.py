from typing import Any

from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models import Configuration

from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.checker import ConsistencyChecker
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.diagnosis_model import DiagnosisModel

from flamapy.metamodels.pysat_metamodel.operations.diagnosis.fastdiag import FastDiag


class Glucose3FastDiag(Operation):

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

    def is_valid(self) -> bool:
        pass

    def get_result(self) -> list[str]:
        return self.diagnosis_messages

    def execute(self, model: PySATModel) -> 'Glucose3FastDiag':
        # transform model to diagnosis model
        diag_model = DiagnosisModel(model)
        diag_model.prepare_diagnosis_task(configuration=self.configuration, test_case=self.test_case)

        print(f'C: {diag_model.get_C()}')
        print(f'B: {diag_model.get_B()}')

        checker = ConsistencyChecker(self.solverName, diag_model.get_KB())
        fastdiag = FastDiag(checker)

        C = diag_model.get_C()
        if self.configuration is None:
            C.reverse()  # reverse the list to get the correct order of diagnosis

        diag = fastdiag.findDiagnosis(C, diag_model.get_B())

        if diag:
            mess = f'Diagnosis: ['
            mess += diag_model.get_diagnosis(diag)
            mess += ']'
            self.diagnosis_messages.append(mess)

        checker.delete()

        return self
