from pysat.solvers import Glucose3

from flamapy.core.operations import ProductsNumber
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3ProductsNumber(ProductsNumber):

    def __init__(self) -> None:
        self.products_number = 0
        self.solver = Solver(name='glucose3')

    def get_products_number(self) -> int:
        return self.products_number

    def get_result(self) -> int:
        return self.get_products_number()

    def execute(self, model: PySATModel) -> 'Glucose3ProductsNumber':
        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        for _ in self.solver.enum_models():
            self.products_number += 1
        self.solver.delete()
        return self
