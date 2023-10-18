from flamapy.metamodels.configuration_metamodel.models import Configuration

from flamapy.metamodels.pysat_metamodel.models import PySATModel


class DiagnosisModel(PySATModel):
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
        return 'pysat_diagnosis'

    def __init__(self) -> None:
        super().__init__()
        # set of constraints which could be faulty
        self.set_c = []
        # background knowledge (i.e., the knowledge that is known to be true)
        self.set_b = []
        # set of all CNF with added assumptions
        self.set_kb = []
        # map clauses to relationships/constraint
        self.constraint_map: list[(str, list[list[int]])] = []

        self.constraint_assumption_map = {}

    def add_clause_to_map(self, description: str, clauses: list[list[int]]) -> None:
        self.constraint_map.append((description, clauses))

    def get_c(self) -> list:
        return self.set_c

    def get_b(self) -> list:
        return self.set_b

    def get_kb(self) -> list:
        return self.set_kb

    def get_pretty_diagnoses(self, assumptions: list[list[int]]) -> str:
        diagnoses = []
        for ass in assumptions:
            diag = []
            for item in ass:
                if self.constraint_assumption_map[item]:
                    diag.append(self.constraint_assumption_map[item])
            diagnoses.append(f"[{', '.join(diag)}]")

        return ','.join(diagnoses)

    def prepare_diagnosis_task(self, configuration: Configuration = None,
                               test_case: Configuration = None) -> None:
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
            self._prepare_assumptions(configuration=configuration)
        else:
            if test_case is None:
                # Diagnosis the feature model
                # C = CF (i.e., = PySATModel - {f0 = true})
                # B = {f0 = true}
                self._prepare_assumptions()
            else:
                # Diagnosis the error
                # C = CF (i.e., = PySATModel - {f0 = true})
                # B = {f0 = true} + test_case
                self._prepare_assumptions(test_case=test_case)

    def prepare_redundancy_detection_task(self) -> None:
        """
        This function prepares the model for WipeOutR algorithm.
        Execute this method after the model is built.
        C = CF (i.e., = PySATModel - {f0 = true})
        B = {}
        """
        # C = CF (i.e., = PySATModel - {f0 = true})
        self.set_c = self._prepare_assumptions
        self.set_b = []  # B = {}
        # ToDo: TBD

    def _prepare_assumptions(self, configuration: Configuration = None,
                             test_case: Configuration = None) -> None:
        assumption = []

        id_assumption = len(self.variables) + 1
        id_assumption = self._prepare_assumptions_for_kb(assumption, id_assumption)

        start_id_configuration = len(assumption)
        if configuration is not None:
            self.constraint_assumption_map = {}  # reset the map
            id_assumption = self._prepare_assumptions_for_configuration(assumption,
                                                                        configuration,
                                                                        id_assumption)

        start_id_test_case = len(assumption)
        if test_case is not None:
            self._prepare_assumptions_for_configuration(assumption, test_case,
                                                        id_assumption)

        if configuration is not None:
            self.set_b = assumption[:start_id_configuration]
            self.set_c = assumption[start_id_configuration:]
        else:
            if test_case is not None:
                self.set_b = [assumption[0]] + assumption[start_id_test_case:]
                self.set_c = assumption[1:start_id_test_case]
            else:
                self.set_b = [assumption[0]]
                self.set_c = assumption[1:]

    def _prepare_assumptions_for_kb(self, assumption, id_assumption):
        cstr_map = self.constraint_map
        # loop through all tuples in the constraint map
        for _, map_item in enumerate(cstr_map):
            # get description
            desc = map_item[0]
            # get clauses
            clauses = map_item[1]
            # loop through all variables in the constraint
            for _, clause in enumerate(clauses):
                # add the assumption variable to the clause
                # assumption => clause
                # i.e., -assumption v clause
                clause.append(-1 * id_assumption)

            assumption.append(id_assumption)
            self.set_kb.extend(clauses)
            self.constraint_assumption_map[id_assumption] = desc

            id_assumption += 1

        return id_assumption

    def _prepare_assumptions_for_configuration(self, assumption,
                                               configuration, id_assumption):
        config = [feat.name for feat in configuration.elements]
        for feat in config:
            if feat not in self.variables.keys():
                raise KeyError(f'Feature {feat} is not in the model.')

        for feat in configuration.elements.items():
            desc = ''
            clause = []

            if feat[1]:
                desc = f'{feat[0].name} = true'
                clause = [self.variables[feat[0].name], -1 * id_assumption]
            elif not feat[1]:
                desc = f'{feat[0].name} = false'
                clause = [-1 * self.variables[feat[0].name], -1 * id_assumption]

            assumption.append(id_assumption)
            self.set_kb.append(clause)
            self.constraint_assumption_map[id_assumption] = desc

            id_assumption += 1

        return id_assumption
