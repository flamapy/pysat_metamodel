"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/checker/ChocoConsistencyChecker.java
"""

from pysat.solvers import Solver


class ConsistencyChecker:

    def __init__(self, solverName: str, KB: list) -> None:
        self.solver = None
        self.result = False

        self.solver = Solver(solverName, bootstrap_with=KB)

    def is_consistent(self, C: list, Δ: list) -> bool:
        """
        Check if the given CNF formula is consistent using a solver.
        :param C: a list of assumptions should be added to the CNF formula
        :param Δ: a list of assumptions should not be added to the CNF formula
        :return: a boolean value indicating whether the given CNF formula is consistent
        """
        assumptions = C + [-1 * item for item in Δ]
        self.result = self.solver.solve(assumptions=assumptions)
        # print(f"assumptions: {assumptions} - result: {self.result}")
        return self.result

    def delete(self):
        self.solver.delete()
