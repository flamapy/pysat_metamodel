from typing import cast

from pysat.solvers import Solver

from flamapy.core.operations import ValidConfiguration
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATValidConfiguration(ValidConfiguration):

    def __init__(self) -> None:
        self.result = False
        self.configuration = Configuration({})
        self.solver = Solver(name='glucose3')

    def is_valid(self) -> bool:
        return self.result

    def get_result(self) -> bool:
        return self.is_valid()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: VariabilityModel) -> 'PySATValidConfiguration':
        model = cast(PySATModel, model)

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        assumptions = []
        for feat in self.configuration.elements.items():
            if feat[1]:
                assumptions.append(model.variables[feat[0].name])
            elif not feat[1]:
                assumptions.append(-model.variables[feat[0].name])

        self.result = self.solver.solve(assumptions=assumptions)
        self.solver.delete()
        return self
