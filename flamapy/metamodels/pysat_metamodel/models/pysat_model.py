from pysat.formula import CNF

from flamapy.core.models import VariabilityModel


class PySATModel(VariabilityModel):

    @staticmethod
    def get_extension() -> str:
        return 'pysat'

    def __init__(self) -> None:
        # self.r_cnf = CNF()  # ToDo: This should be avoid
        # self.ctc_cnf = CNF()  # ToDo: This should be avoid
        self._cnf = CNF()
        self.variables: dict[str, int] = {}  # feature's name -> id
        self.features: dict[int, str] = {}  # id -> feature's name

        self.constraint_map: list[(str, list[list[int]])] = []  # map clauses to relationships/constraint

    def add_clause(self, clause: list[int]) -> None:
        # self.ctc_cnf.append(clause)
        self._cnf.append(clause)

    def add_clause_toMap(self, description: str, clauses: list[list[int]]) -> None:
        self.constraint_map.append((description, clauses))

    def get_all_clauses(self) -> CNF:
        # clauses = CNF()
        # clauses.extend(self.r_cnf.clauses)
        # clauses.extend(self.ctc_cnf.clauses)
        # return clauses
        return self._cnf

    def get_constraint_map(self) -> list:
        return self.constraint_map
