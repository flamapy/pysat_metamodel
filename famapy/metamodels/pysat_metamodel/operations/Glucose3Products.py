from pysat.solvers import Glucose3
from pysat_metamodel.model.PySATModel import PySATModel

from famapy.core.operations.Products import ProductsOperation


class Glucose3Products(ProductsOperation):
    def __init__(self):
        self.products = list()

    def execute(self, model):
        g = Glucose3()
        for clause in model.cnf:  # AC es conjunto de conjuntos
            g.add_clause(clause)  # añadimos la constraint

        for solutions in g.enum_models():
            product=list()
            for variable in solutions :
                if (variable > 0) : #This feature should appear in the product
                    product.append(model.features.get(variable))
            self.products.append(product)

    def getProducts(self):
        return self.products
