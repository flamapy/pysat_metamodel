from famapy.core.operations import Valid
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat.solvers import Glucose3


class Glucose3Valid(Valid):

    def __init__(self):
        self.result = False

    def is_valid(self):
        return self.result

    def get_result(self):
        return self.is_valid()

    def execute(self, model: PySATModel) -> 'Glucose3Valid':
        glucose = Glucose3()

        for clause in model.r_cnf:
            glucose.add_clause(clause)
        for clause in model.ctc_cnf:
            glucose.add_clause(clause)

        self.result = glucose.solve()
        glucose.delete()
        return self
