from pysat.solvers import Glucose3

from flamapy.core.operations import ValidConfiguration
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3ValidConfiguration(ValidConfiguration):

    def __init__(self) -> None:
        self.result = False
        self.configuration = Configuration({})

    def is_valid(self) -> bool:
        return self.result

    def get_result(self) -> bool:
        return self.is_valid()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: PySATModel) -> 'Glucose3ValidConfiguration':
        glucose = Glucose3()

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            glucose.add_clause(clause)  # añadimos la constraint

        assumptions = []
        for feat in self.configuration.elements.items():
            if feat[1]:
                assumptions.append(model.variables[feat[0].name])
            elif not feat[1]:
                assumptions.append(-model.variables[feat[0].name])

        self.result = glucose.solve(assumptions=assumptions)
        glucose.delete()
        return self
