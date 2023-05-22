from typing import Any

# from pysat.solvers import Solver

from flamapy.core.operations import ErrorDiagnosis, Operation
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel, ConsistencyChecker, diff, split

import logging


class Glucose3QuickXPlain(ErrorDiagnosis):

    def __init__(self) -> None:
        self.result = False
        self.configuration = None
        # self.solver = Solver(name='glucose3')
        self.solverName = 'glucose3'
        self.diagnosis_messages: list[str] = []

        self.checker = None

    def get_diagnosis_messages(self) -> list[Any]:
        return self.get_result()

    # if specify configuration -> C=configuration
    # otherwise -> C=PySATModel
    # def set_configuration(self, configuration: Configuration) -> None:
    #     self.configuration = configuration
    #     print(self.configuration)

    def get_result(self) -> list[str]:
        return self.diagnosis_messages

    def execute(self, model: PySATModel) -> 'Glucose3QuickXPlain':
        model.prepare_diagnosis_task(configuration=self.configuration)

        print("C")
        print(model.get_C())
        print("B")
        print(model.get_B())

        checker = ConsistencyChecker(self.solverName)
        quickxplain = QuickXPlain(checker)

        cs = quickxplain.quickXplain(model.get_C(), model.get_B())

        if cs:
            self.diagnosis_messages.append(f'Conflicts: {cs}')
        # print("Diagnosis")
        # print(diag)

        # CandB = model.get_C() + model.get_B()
        #
        # print("C+B")
        # print(CandB)
        #
        # self.result = checker.is_consistent(CandB)
        # if not self.result:
        #     print("Model is not consistent")
        # else:
        #     print("Model is consistent")

        return self

        # assumptions = []
        #
        # if self.configuration is None:
        #     print("Clauses")
        #     for clause in model.get_all_clauses():
        #         print(clause)
        #
        #     id = len(model.variables) + 1
        #     for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
        #         # add a selector variable to each clause
        #         clause.append(id)
        #         # print(clause)
        #         assumptions.append(id)
        #         id += 1
        #         self.solver.add_clause(clause)  # añadimos la constraint
        #
        # print("New Clauses")
        # for clause in model.get_all_clauses():
        #     print(clause)
        #
        # # print assumptions
        # print("Assumptions")
        # print(assumptions)
        # print(self.solver.solve())

        # core_features = []
        # if glucose.solve():
        #     for variable in model.variables.items():
        #         if not glucose.solve(assumptions=[-variable[1]]):
        #             core_features.append(variable[0])

        # self.result = self.is_consistent(assumptions)
        # self.solver.delete()
        # return self


class QuickXPlain:

    def __init__(self, checker: ConsistencyChecker) -> None:
        self.checker = checker

    def quickXplain(self, C, B):
        if self.checker.is_consistent(B + C):
            return []
        elif len(C) == 0:
            return []
        else:
            return self.QX(C, B, [])

    def QX(self, C, B, Bo):
        if len(Bo) != 0 and not self.checker.is_consistent(B):
            return []

        if len(C) == 1:
            return C

        # k = int(len(C) / 2)
        # Ca = C[0:k]
        # Cb = C[k:len(C)]
        Ca, Cb = split(C)

        A2 = self.QX(Ca, (B + Cb), Cb)
        A1 = self.QX(Cb, (B + A2), A2)

        return A1 + A2
