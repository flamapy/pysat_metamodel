from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.pysat_metamodel.models import PySATModel


class DiagnosisModel(object):
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

    # @staticmethod
    # def get_extension() -> str:
    #     return 'pysat'

    def __init__(self, model: PySATModel) -> None:
        # super().__init__()
        self.model = model
        self.C = None  # set of constraints which could be faulty
        self.B = None  # background knowledge (i.e., the knowledge that is known to be true)

    def get_C(self) -> list:
        return self.C

    def get_B(self) -> list:
        return self.B

    def prepare_diagnosis_task(self, configuration: Configuration = None, test_case: Configuration = None) -> None:
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
            self.B = self.model.get_all_clauses().clauses.copy()
        else:
            if test_case is None:
                # Diagnosis the feature model
                # C = CF (i.e., = PySATModel - {f0 = true})
                self.C = self.get_CF()
                # B = {f0 = true}
                self.B = []
                self.B.append(self.get_root_constraint())
            else:
                # Diagnosis the error
                # C = CF (i.e., = PySATModel - {f0 = true})
                self.C = self.get_CF()
                # B = {f0 = true} + test_case
                self.B = []
                self.B.append(self.get_root_constraint())
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
        self.B = []  # B = {}
        # ToDo: TBD

    def get_CF(self) -> list:
        """
        Get the constraint set CF of the feature model.
        """
        cnf = self.model.get_all_clauses().copy()
        del cnf.clauses[0]  # remove the root constraint (i.e., f0 = true)
        # reverse order of clauses
        cnf.clauses.reverse()
        return cnf.clauses

    def get_root_constraint(self) -> list[int]:
        """
        Get the root constraint (i.e., f0 = true).
        """
        return self.model.get_all_clauses().clauses[0].copy()

    def configuration_to_cnf(self, configuration: Configuration) -> list:
        """
        Convert a configuration to a list of clauses.
        """
        cnf = []

        config: list[str] = []
        if configuration is not None:
            config = [feat.name for feat in configuration.elements]

        # for feat in config:
        #     if feat not in self.variables.keys():
        #         return None

        for feat in config:
            if configuration.elements[feat] is True:
                cnf.append([self.model.variables[feat]])
            else:
                cnf.append([-self.model.variables[feat]])

        return cnf
