from pysat.formula import CNF
from pysat.solvers import Glucose3

from famapy.core.models.VariabilityModel import VariabilityModel


class PySATModel(VariabilityModel):

    def __init__(self):
        self.cnf = CNF()
        self.variables = {}
        self.features = {}

    def add_constraint(self, constraint):
        self.cnf.append(constraint)
