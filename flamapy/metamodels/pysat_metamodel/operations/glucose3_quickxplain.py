from typing import Any

from flamapy.core.operations import ErrorDiagnosis
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel, ConsistencyChecker, diff, split

import logging


class Glucose3QuickXPlain(ErrorDiagnosis):

    def __init__(self) -> None:
        self.result = False
        self.configuration = None
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

        cs = quickxplain.findConflictSet(model.get_C(), model.get_B())

        if cs:
            self.diagnosis_messages.append(f'Conflicts: {cs}')

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
    """
    Implementation of QuickXPlain algorithm
    Junker, Ulrich. "Quickxplain: Conflict detection for arbitrary constraint propagation algorithms."
    IJCAI’01 Workshop on Modelling and Solving problems with constraints. Vol. 4. 2001.
    """

    def __init__(self, checker: ConsistencyChecker) -> None:
        self.checker = checker

    def findConflictSet(self, C: list, B: list) -> list:
        """
        // Func QuickXPlain(C={c1,c2,…, cm}, B): CS
        // IF consistent(B∪C) return "No conflict";
        // IF isEmpty(C) return Φ;
        // ELSE return QX(Φ, C, B);
        :param C: a consideration set
        :param B: a background knowledge
        :return: a conflict set or an empty set
        """
        logging.debug(f'quickXPlain [C={C}, B={B}]')

        # if C is empty or consistent(B U C) then return empty set
        if len(C) == 0 or self.checker.is_consistent(B + C):
            logging.debug('return Φ')
            return []
        else:  # return QX(Φ, C, B)
            cs = self.qx([], C, B)

            logging.debug(f'return {cs}')
            return cs

    def qx(self, D: list, C: list, B: list) -> list:
        """
        // func QX(Δ, C={c1,c2, …, cq}, B): CS
        // IF (Δ != Φ AND inconsistent(B)) return Φ;
        // IF singleton(C) return C;
        // k = q/2;
        // C1 <-- {c1, …, ck}; C2 <-- {ck+1, …, cq};
        // CS1 <-- QX(C2, C1, B ∪ C2);
        // CS2 <-- QX(CS1, C2, B ∪ CS1);
        // return (CS1 ∪ CS2)
        :param D: check to skip redundant consistency checks
        :param C: a consideration set of constraints
        :param B: a background knowledge
        :return: a conflict set or an empty set
        """
        logging.debug(f'>>> QX [D={D}, C={C}, B={B}]')

        # if D != Φ and inconsistent(B) then return Φ
        if len(D) != 0 and not self.checker.is_consistent(B):
            logging.debug('<<< return Φ')
            return []

        # if C is singleton then return C
        if len(C) == 1:
            logging.debug(f'<<< return {C}')
            return C

        # C1 = {c1..ck}; C2 = {ck+1..cn};
        C1, C2 = split(C)

        # CS1 = QX(C2, C1, B U C2)
        CS1 = self.qx(C2, C1, (B + C2))
        # CS2 = QX(CS1, C2, B U CS1)
        CS2 = self.qx(CS1, C2, (B + CS1))

        logging.debug(f'<<< return [CS1={CS1} U CS2={CS2}]')

        # return CS1 U CS2
        return CS1 + CS2
