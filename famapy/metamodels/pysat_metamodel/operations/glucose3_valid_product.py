from pysat.solvers import Glucose3

from famapy.core.operations import ValidProduct
from famapy.metamodels.pysat_metamodel.models.configuration import PySATConfiguration
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

class Glucose3ValidProduct(ValidProduct):

    def __init__(self):
        self.result = False
        self.configuration = None

    def is_valid(self):
        return self.result

    def get_result(self):
        return self.is_valid()

    def set_configuration(self, configuration: PySATConfiguration):
        self.configuration = configuration

    def execute(self, model: PySATModel) -> 'Glucose3ValidProduct':
        g = Glucose3()
        for clause in model.r_cnf:
            g.add_clause(clause)
        for clause in model.ctc_cnf:
            g.add_clause(clause)

        assumptions = []
        config = [feat.name for feat in self.configuration.elements]
        for feat in model.features.values():
            if feat in config:
                assumptions.append(model.variables[feat])
            else:
                assumptions.append(-model.variables[feat])

        self.result = g.solve(assumptions=assumptions)
        g.delete()
        return self
