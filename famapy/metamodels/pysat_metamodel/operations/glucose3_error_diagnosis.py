#from pysat.solvers import Glucose3

from famapy.core.operations import ErrorDiagnosis
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3ErrorDiagnosis(ErrorDiagnosis):

    def __init__(self) -> None:
        self.diagnosis_messages: list[str] = []

    def get_diagnosis_messages(self) -> list[str]:
        return self.diagnosis_messages

    def get_result(self) -> list[str]:
        return self.get_diagnosis_messages()

    def execute(self, model: PySATModel) -> 'Glucose3ErrorDiagnosis': # noqa: MC0001
        return self
        # TODO: reimplement without splitting clauses.
        # glucose_r = Glucose3()
        # glucose_r_ctc = Glucose3()
        # for clause in model.r_cnf:
        #     glucose_r.add_clause(clause)
        #     glucose_r_ctc.add_clause(clause)
        # for clause in model.ctc_cnf:
        #     glucose_r_ctc.add_clause(clause)

        # if glucose_r_ctc.solve():
        #     dead_features = []
        #     for feat in model.features:
        #         if not glucose_r_ctc.solve(assumptions=[feat]):
        #             dead_features.append(feat)

        #     false_optional_features = []
        #     assumption = 1
        #     for feat in model.features:
        #         if (not glucose_r_ctc.solve(assumptions=[-feat]) and
        #                 glucose_r.solve(assumptions=[-feat])):
        #             if glucose_r.solve(assumptions=[assumption, -feat]):
        #                 false_optional_features.append(feat)
        #             assumption = feat

        #     diagnosis = []
        #     for dead in dead_features:
        #         name = model.features.get(dead)
        #         for clause in model.ctc_cnf:
        #             if clause[1] == -dead:
        #                 if clause[0] < 0:
        #                     diagnosis.append(
        #                         'For dead feature ' +
        #                         name + ': ' +
        #                         model.features.get(-clause[0]) +
        #                         ' excludes ' +
        #                         name
        #                     )
        #                 else:
        #                     diagnosis.append(
        #                         'For dead feature ' +
        #                         name +
        #                         ': ' +
        #                         model.features.get(clause[0]) +
        #                         ' requires ' +
        #                         name
        #                     )
        #             if clause[0] == -dead:

        #                 if clause[1] < 0:
        #                     diagnosis.append(
        #                         'For dead feature ' +
        #                         name +
        #                         ': ' +
        #                         name +
        #                         ' excludes ' +
        #                         model.features.get(-clause[1])
        #                     )
        #                 else:
        #                     diagnosis.append(
        #                         'For dead feature ' +
        #                         name +
        #                         ': ' +
        #                         name +
        #                         ' requires ' +
        #                         model.features.get(clause[1])
        #                     )

        #     for false in false_optional_features:
        #         name = model.features.get(false)
        #         for clause in model.ctc_cnf:
        #             if clause[1] == false:
        #                 if clause[0] < 0:
        #                     diagnosis.append(
        #                         'For false optional feature ' +
        #                         name + ': ' +
        #                         model.features.get(-clause[0]) +
        #                         ' requires ' +
        #                         name
        #                     )
        #                 else:
        #                     diagnosis.append(
        #                         'For false optional feature ' +
        #                         name +
        #                         ': ' +
        #                         model.features.get(clause[0]) +
        #                         ' excludes ' +
        #                         name
        #                     )
        #             if clause[0] == false:
        #                 if clause[1] < 0:
        #                     diagnosis.append(
        #                         'For false optional feature ' +
        #                         name +
        #                         ': ' +
        #                         name +
        #                         ' requires ' +
        #                         model.features.get(-clause[1])
        #                     )
        #                 else:
        #                     diagnosis.append(
        #                         'For false optional feature ' +
        #                         name +
        #                         ': ' +
        #                         name +
        #                         ' excludes ' +
        #                         model.features.get(clause[1])
        #                     )

        #     for message in diagnosis:
        #         if message not in self.diagnosis_messages:
        #             self.diagnosis_messages.append(message)

        # else:
        #     for clause in model.ctc_cnf:
        #         if clause[0] < 0 and clause[1] < 0:
        #             self.diagnosis_messages.append(
        #                 model.features.get(-clause[0]) +
        #                 ' excludes ' +
        #                 model.features.get(-clause[1])
        #             )

        # glucose_r.delete()
        # glucose_r_ctc.delete()
        # return self
