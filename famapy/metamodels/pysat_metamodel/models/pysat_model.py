from pysat.formula import CNF

from famapy.core.models import VariabilityModel


class PySATModel(VariabilityModel):

    @staticmethod
    def get_extension():
        return 'pysat'

    def __init__(self):
        self.r_cnf = CNF()
        self.ctc_cnf = CNF()
        self.variables = {}
        self.features = {}

    def add_constraint(self, constraint):
        self.ctc_cnf.append(constraint)

    def get_all_clauses(self):
        clauses = CNF()
        clauses.extend(self.r_cnf.clauses)
        clauses.extend(self.ctc_cnf.clauses)
        return clauses