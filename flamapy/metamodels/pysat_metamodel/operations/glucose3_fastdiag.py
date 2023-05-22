from typing import Any

from flamapy.core.operations import ErrorDiagnosis
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel, ConsistencyChecker, diff, split

import logging


class Glucose3FastDiag(ErrorDiagnosis):

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

    def execute(self, model: PySATModel) -> 'Glucose3FastDiag':
        model.prepare_diagnosis_task(configuration=self.configuration)

        print("C")
        print(model.get_C())
        print("B")
        print(model.get_B())

        checker = ConsistencyChecker(self.solverName)
        fastdiag = FastDiag(checker)

        diag = fastdiag.findDiagnosis(model.get_C(), model.get_B())

        if diag:
            self.diagnosis_messages.append(f'Diagnosis: {diag}')

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


class FastDiag:
    """
    Implementation of MSS-based FastDiag algorithm.
    Le, V. M., Silva, C. V., Felfernig, A., Benavides, D., Galindo, J., & Tran, T. N. T. (2023).
    FastDiagP: An Algorithm for Parallelized Direct Diagnosis.
    arXiv preprint arXiv:2305.06951.
    """

    def __init__(self, checker: ConsistencyChecker) -> None:
        self.checker = checker

    def findDiagnosis(self, C: list, B: list) -> list:
        """
        Activate FastDiag algorithm if there exists at least one constraint,
        which induces an inconsistency in B. Otherwise, it returns an empty set.

        // Func FastDiag(C, B) : Δ
        // if isEmpty(C) or consistent(B U C) return Φ
        // else return C \\ FD(Φ, C, B)
        :param C: a consideration set of constraints
        :param B: a background knowledge
        :return: a diagnosis or an empty set
        """
        logging.debug(f'fastDiag [C={C}, B={B}]')

        # if isEmpty(C) or consistent(B U C) return Φ
        if len(C) == 0 or self.checker.is_consistent(B + C):
            logging.debug('return Φ')
            return []
        else:  # return C \ FD(C, B, Φ)
            mss = self.fd([], C, B)
            diag = diff(C, mss)

            logging.debug(f'return {diag}')
            return diag

    def fd(self, Δ: list, C: list, B: list) -> list:
        """
        The implementation of MSS-based FastDiag algorithm.
        The algorithm determines a maximal satisfiable subset MSS (Γ) of C U B.

        // Func FD(Δ, C = {c1..cn}, B) : MSS
        // if Δ != Φ and consistent(B U C) return C;
        // if singleton(C) return Φ;
        // k = n/2;
        // C1 = {c1..ck}; C2 = {ck+1..cn};
        // Δ1 = FD(C2, C1, B);
        // Δ2 = FD(C1 - Δ1, C2, B U Δ1);
        // return Δ1 ∪ Δ2;
        :param Δ: check to skip redundant consistency checks
        :param C: a consideration set of constraints
        :param B: a background knowledge
        :return: a maximal satisfiable subset MSS of C U B
        """
        logging.debug(f'>>> FD [Δ={Δ}, C={C}, B={B}]')

        # if Δ != Φ and consistent(B U C) return C;
        if len(Δ) != 0 and self.checker.is_consistent(B + C):
            logging.debug(f'<<< return {C}')
            return C

        # if singleton(C) return Φ;
        if len(C) == 1:
            logging.debug('<<< return Φ')
            return []

        # C1 = {c1..ck}; C2 = {ck+1..cn};
        C1, C2 = split(C)

        # Δ1 = FD(C2, C1, B);
        Δ1 = self.fd(C2, C1, B)
        # Δ2 = FD(C1 - Δ1, C2, B U Δ1);
        C1withoutΔ1 = diff(C1, Δ1)
        Δ2 = self.fd(C1withoutΔ1, C2, B + Δ1)

        logging.debug('<<< return [Δ1={Δ1} ∪ Δ2={Δ2}]')

        # return Δ1 + Δ2
        return Δ1 + Δ2
