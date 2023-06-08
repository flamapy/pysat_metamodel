from pysat.formula import CNF

from flamapy.core.models import VariabilityModel


class PySATModel(VariabilityModel):

    @staticmethod
    def get_extension() -> str:
        return 'pysat'

    def __init__(self) -> None:
        #self.r_cnf = CNF()  # ToDo: This should be avoid
        #self.ctc_cnf = CNF()  # ToDo: This should be avoid
        self._cnf = CNF()
        self.variables: dict[str, int] = {}  # feature's name -> id
        self.features: dict[int, str] = {}  # id -> feature's name

    def add_clause(self, clause: list[int]) -> None:
        #self.ctc_cnf.append(clause)
        self._cnf.append(clause)

    def get_all_clauses(self) -> CNF:
        #clauses = CNF()
        #clauses.extend(self.r_cnf.clauses)
        #clauses.extend(self.ctc_cnf.clauses)
        #return clauses
        return self._cnf
