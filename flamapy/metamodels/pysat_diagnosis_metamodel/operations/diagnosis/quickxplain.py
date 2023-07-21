"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/QuickXPlain.java
"""

import logging

from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.checker import ConsistencyChecker
from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.utils import split


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
        # print(f'quickXPlain [C={C}, B={B}]')

        # if C is empty or consistent(B U C) then return empty set
        if len(C) == 0 or self.checker.is_consistent(B + C, []):
            logging.debug('return Φ')
            # print('return Φ')
            return []
        else:  # return QX(Φ, C, B)
            cs = self.qx([], C, B)

            logging.debug(f'return {cs}')
            # print(f'return {cs}')
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
        if len(D) != 0 and not self.checker.is_consistent(B, C):
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
