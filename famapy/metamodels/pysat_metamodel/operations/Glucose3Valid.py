from pysat.solvers import Glucose3

from famapy.core.operations.Valid import Valid
from famapy.metamodels.pysat_metamodel.models.PySATModel import PySATModel


class Glucose3Valid(Valid):

    def execute(self, model: PySATModel) -> 'Glucose3Valid':
        g = Glucose3()
        for clause in model.cnf:  # AC es conjunto de conjuntos
            g.add_clause(clause)  # añadimos la constraint
        self.res = g.solve()
        return super().execute(model)
