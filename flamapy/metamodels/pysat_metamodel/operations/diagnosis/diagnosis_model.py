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
        self.model = model
        self.C = None  # set of constraints which could be faulty
        self.B = None  # background knowledge (i.e., the knowledge that is known to be true)

        # KB = list of (constraint, CNF, id_assumption)
        self.KB = None

    def get_C(self) -> list:
        return self.C

    def get_B(self) -> list:
        return self.B

    def get_KB(self) -> list:
        """
        Return all CNF in KB
        """
        cnf = [item[1] for item in self.KB]
        flat_list = [item for sublist in cnf for item in sublist]

        return flat_list

    def get_diagnosis(self, assumptions: list[int]) -> str:
        diag = []
        for ass in assumptions:
            for cstr in self.KB:
                if ass == cstr[2]:
                    diag.append(cstr[0])
                    break

        return ','.join(diag)

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
                self.C, self.B, self.KB = self.get_CF()
                # B = {f0 = true}
                # self.B = []
                # self.B.append(self.get_root_constraint())
            else:
                # Diagnosis the error
                # C = CF (i.e., = PySATModel - {f0 = true})
                self.C = self.get_CF
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
        self.C = self.get_CF
        self.B = []  # B = {}
        # ToDo: TBD

    def get_CF(self) -> (list, list, list):
        """
        Get the constraint set CF of the feature model.
        """
        constraint_map: list[(str, list[list[int]], int)] = []
        c_map = self.model.get_constraint_map().copy()

        assumption = []
        # loop through all tuples in the constraint map
        id_assumption = len(self.model.variables) + 1
        for i in range(len(c_map)):
            # get description
            desc = c_map[i][0]
            # get clauses
            clauses = c_map[i][1]
            # loop through all variables in the constraint
            for j in range(len(clauses)):
                # get each clause
                clause = clauses[j]
                # add the assumption variable to the clause
                # assumption => clause
                # i.e., -assumption v clause
                clause.append(-1 * id_assumption)

            constraint_map.append((desc, clauses, id_assumption))

            assumption.append(id_assumption)
            id_assumption += 1

        # for cstr in constraint_map:
        #     print(cstr)

        B = assumption[0]
        del assumption[0]  # remove the root constraint (i.e., f0 = true)
        # reverse order of assumption
        assumption.reverse()
        return assumption, [B], constraint_map

    def get_root_constraint(self) -> (str, list):
        """
        Get the root constraint (i.e., f0 = true).
        """
        return self.model.get_constraint_map()[0]

    def configuration_to_cnf(self, configuration: Configuration) -> list:
        """
        Convert a configuration to a list of clauses.
        """
        cnf = []

        config: list[str] = []
        if configuration is not None:
            config = [feat.name for feat in configuration.elements]

        for feat in config:
            if feat not in self.model.variables.keys():
                raise Exception(f'Feature {feat} is not in the model.')

        for feat in configuration.elements.items():
            if feat[1]:
                cnf.append([self.model.variables[feat[0].name]])
            elif not feat[1]:
                cnf.append([-self.model.variables[feat[0].name]])

        return cnf
