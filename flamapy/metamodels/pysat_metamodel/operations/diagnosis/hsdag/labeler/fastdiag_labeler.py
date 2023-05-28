from dataclasses import dataclass

from flamapy.metamodels.pysat_metamodel.operations.diagnosis.checker import ConsistencyChecker
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.fastdiag import FastDiag
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.hsdag.labeler.labeler import IHSLabelable, LabelerType, \
    AbstractHSParameters


@dataclass
class FastDiagParameters(AbstractHSParameters):
    B: list[int]

    def __str__(self):
        return f"FastDiagParameters{{C={self.C}, D={self.D}, B={self.B}}}"


class FastDiagLabeler(FastDiag, IHSLabelable):

    def __init__(self, checker: ConsistencyChecker, parameters: FastDiagParameters):
        super().__init__(checker)
        self.initial_parameters = parameters

    def get_type(self) -> LabelerType:
        return LabelerType.DIAGNOSIS

    def get_initial_parameters(self) -> AbstractHSParameters:
        return self.initial_parameters

    def get_label(self, parameters: AbstractHSParameters) -> list:
        # params = (FastDiagParameters)parameters
        assert isinstance(parameters, FastDiagParameters), "parameter must be an instance of FastDiagV3Parameters"
        params = parameters
        if len(params.C) > 1 \
                and (len(params.B) == 0 or self.checker.is_consistent(params.B, [])):  # params.D
            diag = self.findDiagnosis(params.C, params.B)
            if len(diag) != 0:
                return [diag]
        return []

    def identify_new_node_parameters(self, param_parent_node: AbstractHSParameters, arcLabel: int) \
            -> AbstractHSParameters:
        assert isinstance(param_parent_node,
                          FastDiagParameters), "parameter must be an instance of FastDiagV3Parameters"
        params = param_parent_node
        C = params.C.copy()
        C.remove(arcLabel)
        B = params.B.copy()
        B.append(arcLabel)
        D = params.D.copy()
        D.append(arcLabel)
        return FastDiagParameters(C, D, B)

    def get_instance(self, checker: ConsistencyChecker):
        return FastDiagLabeler(checker, self.initial_parameters)
