from famapy.core.models.configuration import Configuration
from famapy.core.operations import ValidConfiguration
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat.solvers import Glucose3


class Glucose3ValidConfiguration(ValidConfiguration):

    def __init__(self):
        self.result = False
        self.configuration = None

    def is_valid(self):
        return self.result

    def get_result(self):
        return self.is_valid()

    def set_configuration(self, configuration: Configuration):
        self.configuration = configuration

    def execute(self, model: PySATModel) -> 'Glucose3ValidConfiguration':
        glucose = Glucose3()
        for clause in model.r_cnf:
            glucose.add_clause(clause)
        for clause in model.ctc_cnf:
            glucose.add_clause(clause)

        assumptions = []
        for feat in self.configuration.elements.items():
            if feat[1]:
                assumptions.append(model.variables[feat[0].name])
            elif not feat[1]:
                assumptions.append(-model.variables[feat[0].name])

        self.result = glucose.solve(assumptions = assumptions)
        glucose.delete()
        return self
