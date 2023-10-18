from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.operations import Products
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATProducts(Products):

    def __init__(self) -> None:
        self.products: list[list[Any]] = []
        self.solver = Solver(name='glucose3')

    def get_products(self) -> list[list[Any]]:
        return self.products

    def get_result(self) -> list[list[Any]]:
        return self.get_products()

    def execute(self, model: VariabilityModel) -> 'PySATProducts':
        model = cast(PySATModel, model)

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        for solutions in self.solver.enum_models():
            product = []
            for variable in solutions:
                if variable > 0:
                    product.append(model.features.get(variable))
            self.products.append(product)
        self.solver.delete()
        return self
