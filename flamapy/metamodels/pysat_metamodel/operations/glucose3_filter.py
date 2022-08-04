from typing import Any

from pysat.solvers import Glucose3

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Filter
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3Filter(Filter):

    def __init__(self) -> None:
        self.filter_products: list[list[Any]] = []
        self.configuration = Configuration({})

    def get_filter_products(self) -> list[list[Any]]:
        return self.filter_products

    def get_result(self) -> list[list[Any]]:
        return self.get_filter_products()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: PySATModel) -> 'Glucose3Filter':
        glucose = Glucose3()
        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            glucose.add_clause(clause)  # añadimos la constraint

        assumptions = [
            model.variables.get(feat[0].name) if feat[1]
            else -model.variables.get(feat[0].name)
            for feat in self.configuration.elements.items()
        ]

        for solution in glucose.enum_models(assumptions=assumptions):
            product = []
            for variable in solution:
                if variable > 0:
                    product.append(model.features.get(variable))
            self.filter_products.append(product)
        glucose.delete()
        return self
