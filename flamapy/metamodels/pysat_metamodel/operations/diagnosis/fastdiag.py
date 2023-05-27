import logging

from flamapy.metamodels.pysat_metamodel.operations.diagnosis.utils import split, diff
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.checker import ConsistencyChecker


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
        if len(C) == 0 or self.checker.is_consistent(B + C, []):
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
        if len(Δ) != 0 and self.checker.is_consistent(B + C, Δ):
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
