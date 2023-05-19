from flamapy.metamodels.configuration_metamodel.models import Configuration
from pysat.formula import CNF

from flamapy.core.models import VariabilityModel
from pysat.solvers import Solver


class PySATModel(VariabilityModel):
    """
    This is a new version of the PySATModel class to support the following tasks:
    1. Diagnosis Task
        If a configuration is given:
            C = configuration
            B = {f0 = true} + CF (i.e., = PySATModel)
        else (no configuration is given):
            a. Diagnosis the feature model
                C = CF (i.e., = PySATModel - {f0 = true})
                B = {f0 = true}
            b. Diagnosis the error
                C = CF (i.e., = PySATModel - {f0 = true})
                B = {f0 = true} + test_case
                where test_case is the following:
                + Dead feature: test_case = {fi = true}
                + False optional feature: test_case = {f_parent = true} & {f_child = false}
    2. Redundancy Detection Task (need negative constraints)
        C = CF (i.e., = PySATModel - {f0 = true})
        B = {}
    """

    @staticmethod
    def get_extension() -> str:
        return 'pysat'

    def __init__(self) -> None:
        # self.r_cnf = CNF()  # ToDo: This should be avoid
        # self.ctc_cnf = CNF()  # ToDo: This should be avoid
        self._cnf = CNF()
        self.variables: dict[str, int] = {}  # feature's name -> id
        self.features: dict[int, str] = {}  # id -> feature's name

        self.C = None
        self.B = None

    def add_clause(self, clause: list[int]) -> None:
        # self.ctc_cnf.append(clause)
        self._cnf.append(clause)

    def get_all_clauses(self) -> CNF:
        # clauses = CNF()
        # clauses.extend(self.r_cnf.clauses)
        # clauses.extend(self.ctc_cnf.clauses)
        # return clauses
        return self._cnf

    def get_C(self) -> CNF:
        return self.C

    def get_B(self) -> CNF:
        return self.B

    def prepare_diagnosis_task(self, configuration: Configuration, test_case: Configuration = None) -> None:
        """
        Execute this method after the model is built.
        If a configuration is given:
            C = configuration
            B = {f0 = true} + CF (i.e., = PySATModel)
        else (no configuration is given):
            a. Diagnosis the feature model
                C = CF (i.e., = PySATModel - {f0 = true})
                B = {f0 = true}
            b. Diagnosis the error
                C = CF (i.e., = PySATModel - {f0 = true})
                B = {f0 = true} + test_case
                where test_case is the following:
                + Dead feature: test_case = {fi = true}
                + False optional feature: test_case = {f_parent = true} & {f_child = false}
        """
        if configuration is not None:
            # C = configuration
            self.C = self.configuration_to_cnf(configuration)
            # B = {f0 = true} + CF (i.e., = PySATModel)
            self.B = self._cnf.copy()
        else:
            if test_case is None:
                # Diagnosis the feature model
                # C = CF (i.e., = PySATModel - {f0 = true})
                self.C = self.get_CF()
                # B = {f0 = true}
                self.B = self.get_root_constraint()
            else:
                # Diagnosis the error
                # C = CF (i.e., = PySATModel - {f0 = true})
                self.C = self.get_CF()
                # B = {f0 = true} + test_case
                self.B = self.get_root_constraint()
                self.B.append(self.configuration_to_cnf(test_case))

    def prepare_redundancy_detection_task(self) -> None:
        """
        This function prepares the model for WipeOutR algorithm.
        Execute this method after the model is built.
        C = CF (i.e., = PySATModel - {f0 = true})
        B = {}
        """
        # C = CF (i.e., = PySATModel - {f0 = true})
        self.C = self.get_CF()
        self.B = CNF()  # B = {}
        # ToDo: TBD

    def get_CF(self) -> CNF:
        """
        Get the constraint set CF of the feature model.
        """
        cnf = self._cnf.copy()
        del cnf.clauses[0]  # remove the root constraint (i.e., f0 = true)
        # reverse order of clauses
        cnf.clauses.reverse()
        return cnf

    def get_root_constraint(self) -> CNF:
        """
        Get the root constraint (i.e., f0 = true).
        """
        root_constraint = CNF()
        root_constraint.append(self._cnf.clauses[0])
        return root_constraint

    def configuration_to_cnf(self, configuration: Configuration) -> CNF:
        """
        Convert a configuration to CNF.
        """
        cnf = CNF()

        config: list[str] = []
        if configuration is not None:
            config = [feat.name for feat in configuration.elements]

        # for feat in config:
        #     if feat not in self.variables.keys():
        #         return None

        for feat in config:
            if configuration.elements[feat] is True:
                cnf.append([self.variables[feat]])
            else:
                cnf.append([-self.variables[feat]])

        return cnf


class ConsistencyChecker:

    def __init__(self, solverName: str) -> None:
        self.solver = None
        self.result = False
        self.solverName = solverName

    def is_consistent(self, C: list) -> bool:
        """
        Check if the given CNF formula is consistent using a solver.
        :param C: a list of clauses
        :return: a tuple of two values:
            - a boolean value indicating whether the given CNF formula is consistent
            - the time taken to check the consistency
        """
        self.solver = Solver(name='glucose3')

        for clause in C:
            self.solver.add_clause(clause)

        self.result = self.solver.solve()
        self.solver.delete()
        return self.result


def split(C: list) -> (list, list):
    """
    Splits the given CNF formula into two parts.
    :param C: a list of clauses
    :return: a tuple of two lists
    """
    half_size = len(C) // 2
    return C[:half_size], C[half_size:]
