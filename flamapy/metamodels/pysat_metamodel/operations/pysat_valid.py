from typing import cast

from pysat.solvers import Solver

from flamapy.core.operations import Valid

from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATValid(Valid):

    def __init__(self) -> None:
        self.result = False
        self.solver = Solver(name='glucose3')

    def is_valid(self) -> bool:
        return self.result

    def get_result(self) -> bool:
        return self.is_valid()

    def execute(self, model: VariabilityModel) -> 'PySATValid':
        model = cast(PySATModel, model)

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint
        self.result = self.solver.solve()
        self.solver.delete()
        return self
