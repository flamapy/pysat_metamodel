from pysat.solvers import Glucose3

from famapy.core.models import Configuration
from famapy.core.operations import Filter
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3Filter(Filter):

    def __init__(self):
        self.filter_products = []
        self.configuration = None

    def get_filter_products(self):
        return self.filter_products

    def get_result(self):
        return self.get_filter_products()

    def set_configuration(self, configuration: Configuration):
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
            product = list()
            for variable in solution:
                if variable > 0:
                    product.append(model.features.get(variable))
            self.filter_products.append(product)
        glucose.delete()
        return self
