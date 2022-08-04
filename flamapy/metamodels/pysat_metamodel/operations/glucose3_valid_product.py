from pysat.solvers import Glucose3

from flamapy.core.operations import ValidProduct
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration

from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3ValidProduct(ValidProduct):

    def __init__(self) -> None:
        self.result = False
        self.configuration = Configuration({})

    def is_valid(self) -> bool:
        return self.result

    def get_result(self) -> bool:
        return self.is_valid()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: PySATModel) -> 'Glucose3ValidProduct':
        glucose = Glucose3()
        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            glucose.add_clause(clause)  # añadimos la constraint

        assumptions = []

        config: list[str] = []
        if self.configuration is not None:
            config = [feat.name for feat in self.configuration.elements]

        for feat in config:
            if feat not in model.variables.keys():
                self.result = False
                return self

        for feat in model.features.values():
            if feat in config:
                assumptions.append(model.variables[feat])
            else:
                assumptions.append(-model.variables[feat])

        self.result = glucose.solve(assumptions=assumptions)
        glucose.delete()
        return self
