from famapy.core.models import VariabilityModel
from pysat.formula import CNF


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
