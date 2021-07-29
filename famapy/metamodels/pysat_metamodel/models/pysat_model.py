from typing import Any

from pysat.formula import CNF

from famapy.core.models import VariabilityModel


class PySATModel(VariabilityModel):

    @staticmethod
    def get_extension() -> str:
        return 'pysat'

    def __init__(self) -> None:
        self.r_cnf = CNF()
        self.ctc_cnf = CNF()
        self.variables: dict[str, Any] = {}
        self.features: dict[str, Any] = {}

    def add_clause(self, clause: list[int]) -> None:
        self.ctc_cnf.append(clause)

    def get_all_clauses(self) -> CNF:
        clauses = CNF()
        clauses.extend(self.r_cnf.clauses)
        clauses.extend(self.ctc_cnf.clauses)
        return clauses
