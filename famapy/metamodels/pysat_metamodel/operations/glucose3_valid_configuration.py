from pysat.solvers import Glucose3

from famapy.core.operations import ValidConfiguration
from famapy.metamodels.pysat_metamodel.models.configuration import PySATConfiguration
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel

class Glucose3ValidConfiguration(ValidConfiguration):

    def __init__(self):
        self.result = False
        self.configuration = None

    def is_valid(self):
        return self.result

    def get_result(self):
        return self.is_valid()

    def set_configuration(self, configuration: PySATConfiguration):
        self.configuration = configuration

    def execute(self, model: PySATModel) -> 'Glucose3ValidConfiguration':
        g = Glucose3()
        for clause in model.r_cnf:
            g.add_clause(clause)
        for clause in model.ctc_cnf:
            g.add_clause(clause)

        assumptions = []
        for feat in self.configuration.elements.items():
            if feat[1]:
                assumptions.append(model.variables[feat[0].name])
            elif not feat[1]:
                assumptions.append(-model.variables[feat[0].name])

        self.result = g.solve(assumptions=assumptions)
        g.delete()
        return self
