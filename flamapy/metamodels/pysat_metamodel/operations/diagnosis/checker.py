from pysat.solvers import Solver


class ConsistencyChecker:

    def __init__(self, solverName: str) -> None:
        self.solver = None
        self.result = False
        self.solverName = solverName

    def is_consistent(self, C: list) -> bool:
        """
        Check if the given CNF formula is consistent using a solver.
        :param C: a list of clauses
        :return: a tuple of two values:
            - a boolean value indicating whether the given CNF formula is consistent
            - the time taken to check the consistency
        """
        self.solver = Solver(self.solverName)

        for clause in C:
            self.solver.add_clause(clause)

        self.result = self.solver.solve()
        self.solver.delete()
        return self.result
