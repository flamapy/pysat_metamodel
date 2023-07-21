"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/hs/labeler/FastDiagV3Labeler.java
"""

from dataclasses import dataclass

from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.checker import ConsistencyChecker
from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.fastdiag import FastDiag
from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.hsdag.labeler.labeler import IHSLabelable, LabelerType, AbstractHSParameters


@dataclass
class FastDiagParameters(AbstractHSParameters):
    B: list[int]

    def __str__(self):
        return f"FastDiagParameters{{C={self.C}, B={self.B}}}"


class FastDiagLabeler(FastDiag, IHSLabelable):
    """
    HSLabeler for FastDiag algorithm
    """

    def __init__(self, checker: ConsistencyChecker, parameters: FastDiagParameters):
        super().__init__(checker)
        self.initial_parameters = parameters

    def get_type(self) -> LabelerType:
        return LabelerType.DIAGNOSIS

    def get_initial_parameters(self) -> AbstractHSParameters:
        return self.initial_parameters

    def get_label(self, parameters: AbstractHSParameters) -> list:
        """
        Identifies a diagnosis
        """
        assert isinstance(parameters, FastDiagParameters), "parameter must be an instance of FastDiagParameters"
        neg_C = [-1 * item for item in parameters.C]
        if len(parameters.C) >= 1 \
                and (len(parameters.B) == 0 or self.checker.is_consistent(parameters.B + neg_C, [])):

            diag = self.findDiagnosis(parameters.C, parameters.B)
            if len(diag) != 0:
                return [diag]
        return []

    def identify_new_node_parameters(self, param_parent_node: AbstractHSParameters, arcLabel: int) \
            -> AbstractHSParameters:
        """
        Identifies the new node's parameters on the basis of the parent node's parameters.
        """
        assert isinstance(param_parent_node,
                          FastDiagParameters), "parameter must be an instance of FastDiagParameters"

        C = param_parent_node.C.copy()
        C.remove(arcLabel)
        B = param_parent_node.B.copy()
        B.append(arcLabel)
        # D = param_parent_node.D.copy()
        # D.append(arcLabel)

        return FastDiagParameters(C, [], B)

    def get_instance(self, checker: ConsistencyChecker):
        return FastDiagLabeler(checker, self.initial_parameters)
