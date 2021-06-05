from pysat.solvers import Glucose3

from famapy.core.operations import Valid

from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3Valid(Valid):

    def __init__(self):
        self.result = False

    def is_valid(self):
        return self.result

    def get_result(self):
        return self.is_valid()

    def execute(self, model: PySATModel) -> 'Glucose3Valid':
        glucose = Glucose3()
        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            glucose.add_clause(clause)  # añadimos la constraint
        self.result = glucose.solve()
        glucose.delete()
        return self
