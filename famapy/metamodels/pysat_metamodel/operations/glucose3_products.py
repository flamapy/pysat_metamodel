from pysat.solvers import Glucose3

from famapy.core.operations import Products
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

class Glucose3Products(Products):

    def __init__(self):
        self.products = []

    def get_products(self):
        return self.products

    def get_result(self):
        return self.get_products()

    def execute(self, model: PySATModel) -> 'Glucose3Products':
        g = Glucose3()
        for clause in model.r_cnf:
            g.add_clause(clause)
        for clause in model.ctc_cnf:
            g.add_clause(clause)

        for solutions in g.enum_models():
            product = list()
            for variable in solutions:
                if variable > 0:
                    product.append(model.features.get(variable))
            self.products.append(product)
        g.delete()
        return self
