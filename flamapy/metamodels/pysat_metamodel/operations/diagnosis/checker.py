from pysat.solvers import Solver


class ConsistencyChecker:

    def __init__(self, solverName: str) -> None:
        self.solver = None
        self.result = False
        self.solverName = solverName

    def is_consistent(self, C: list[(str, list[list[int]])]) -> bool:
        """
        Check if the given CNF formula is consistent using a solver.
        :param C: a list of tuples (description, clauses) where clauses is a list of clauses
        :return: a boolean value indicating whether the given CNF formula is consistent
        """
        self.solver = Solver(self.solverName)

        for c in C:
            clauses = c[1]  # c[0] is the description
            for clause in clauses:
                self.solver.add_clause(clause)

        self.result = self.solver.solve()
        self.solver.delete()
        return self.result
