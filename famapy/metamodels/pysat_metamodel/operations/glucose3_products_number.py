from famapy.core.operations import ProductsNumber
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat.solvers import Glucose3


class Glucose3ProductsNumber(ProductsNumber):

    def __init__(self):
        self.products_number = 0

    def get_products_number(self):
        return self.products_number

    def get_result(self):
        return self.get_products_number()

    def execute(self, model: PySATModel) -> 'Glucose3ProductsNumber':
        glucose = Glucose3()
        
        for clause in model.r_cnf:
            glucose.add_clause(clause)
        for clause in model.ctc_cnf:
            glucose.add_clause(clause)

        for _ in glucose.enum_models():
            self.products_number += 1
        glucose.delete()
        return self
