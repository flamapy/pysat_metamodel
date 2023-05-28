from dataclasses import dataclass

from flamapy.metamodels.pysat_metamodel.operations.diagnosis.checker import ConsistencyChecker
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.hsdag.labeler.labeler import IHSLabelable, LabelerType, \
    AbstractHSParameters
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.quickxplain import QuickXPlain


@dataclass
class QuickXPlainParameters(AbstractHSParameters):
    B: list[int]

    def __str__(self):
        return f"QuickXPlainParameters{{C={self.C}, B={self.B}}}"


class QuickXPlainLabeler(QuickXPlain, IHSLabelable):

    def __init__(self, checker: ConsistencyChecker, parameters: QuickXPlainParameters):
        super().__init__(checker)
        self.initial_parameters = parameters

    def get_type(self) -> LabelerType:
        return LabelerType.CONFLICT

    def get_initial_parameters(self) -> AbstractHSParameters:
        return self.initial_parameters

    def get_label(self, parameters: AbstractHSParameters) -> list:
        assert isinstance(parameters, QuickXPlainParameters), "parameter must be an instance of QuickXPlainParameters"

        cs = self.findConflictSet(parameters.C, parameters.B)

        if len(cs) != 0:
            # reverse the order of the conflict set
            cs.reverse()
            return [cs]
        return []

    def identify_new_node_parameters(self, param_parent_node: AbstractHSParameters, arcLabel: int) \
            -> AbstractHSParameters:
        assert isinstance(param_parent_node,
                          QuickXPlainParameters), "parameter must be an instance of QuickXPlainParameters"
        C = param_parent_node.C.copy()
        C.remove(arcLabel)

        B = param_parent_node.B.copy()

        return QuickXPlainParameters(C, B)

    def get_instance(self, checker: ConsistencyChecker):
        return QuickXPlainLabeler(checker, self.initial_parameters)
