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

        self.KB = None  # set of all CNF with added assumptions
        self.constraint_assumption_map = None

    def get_C(self) -> list:
        return self.C

    def get_B(self) -> list:
        return self.B

    def get_KB(self) -> list:
        return self.KB

    def get_diagnosis(self, assumptions: list[int]) -> str:
        diag = []
        for ass in assumptions:
            if self.constraint_assumption_map[ass]:
                diag.append(self.constraint_assumption_map[ass])

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
            # B = {f0 = true} + CF (i.e., = PySATModel)
            self.C, self.B, self.KB, self.constraint_assumption_map = \
                self.prepare_assumptions(configuration=configuration)
        else:
            if test_case is None:
                # Diagnosis the feature model
                # C = CF (i.e., = PySATModel - {f0 = true})
                # B = {f0 = true}
                self.C, self.B, self.KB, self.constraint_assumption_map = self.prepare_assumptions()
            else:
                # Diagnosis the error
                # C = CF (i.e., = PySATModel - {f0 = true})
                # B = {f0 = true} + test_case
                self.C, self.B, self.KB, self.constraint_assumption_map = self.prepare_assumptions(test_case=test_case)

    def prepare_redundancy_detection_task(self) -> None:
        """
        This function prepares the model for WipeOutR algorithm.
        Execute this method after the model is built.
        C = CF (i.e., = PySATModel - {f0 = true})
        B = {}
        """
        # C = CF (i.e., = PySATModel - {f0 = true})
        self.C = self.prepare_assumptions
        self.B = []  # B = {}
        # ToDo: TBD

    def prepare_assumptions(self, configuration: Configuration = None, test_case: Configuration = None) \
            -> (list, list, list, dict):
        assumption = []
        KB = []
        constraint_assumption_map = {}

        id_assumption = len(self.model.variables) + 1
        id_assumption = self.prepare_assumptions_for_KB(KB, assumption, constraint_assumption_map, id_assumption)

        start_id_configuration = len(assumption)
        if configuration is not None:
            constraint_assumption_map = {}  # reset the map
            id_assumption = self.prepare_assumptions_for_configuration(KB, assumption, configuration,
                                                                       constraint_assumption_map,
                                                                       id_assumption)

        start_id_test_case = len(assumption)
        if test_case is not None:
            self.prepare_assumptions_for_configuration(KB, assumption, test_case,
                                                       constraint_assumption_map,
                                                       id_assumption)

        if configuration is not None:
            B = assumption[:start_id_configuration]
            C = assumption[start_id_configuration:]
        else:
            if test_case is not None:
                B = [assumption[0]] + assumption[start_id_test_case:]
                C = assumption[1:start_id_test_case]
            else:
                B = [assumption[0]]
                C = assumption[1:]

        return C, B, KB, constraint_assumption_map

    def prepare_assumptions_for_KB(self, KB, assumption, constraint_assumption_map, id_assumption):
        c_map = self.model.get_constraint_map()
        # loop through all tuples in the constraint map
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

            assumption.append(id_assumption)
            KB.extend(clauses)
            constraint_assumption_map[id_assumption] = desc

            id_assumption += 1

        return id_assumption

    def prepare_assumptions_for_configuration(self, KB, assumption, configuration, constraint_assumption_map,
                                              id_assumption):
        config = [feat.name for feat in configuration.elements]
        for feat in config:
            if feat not in self.model.variables.keys():
                raise Exception(f'Feature {feat} is not in the model.')

        for feat in configuration.elements.items():
            desc = ''
            clause = []

            if feat[1]:
                desc = f'{feat[0].name} = true'
                clause = [self.model.variables[feat[0].name], -1 * id_assumption]
            elif not feat[1]:
                desc = f'{feat[0].name} = false'
                clause = [-1 * self.model.variables[feat[0].name], -1 * id_assumption]

            assumption.append(id_assumption)
            KB.append(clause)
            constraint_assumption_map[id_assumption] = desc

            id_assumption += 1

        return id_assumption
