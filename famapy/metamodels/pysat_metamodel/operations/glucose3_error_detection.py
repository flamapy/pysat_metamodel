from pysat.solvers import Glucose3

from famapy.core.operations import ErrorDetection
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class Glucose3ErrorDetection(ErrorDetection):

    def __init__(self):
        self.errors_messages = []

    def get_errors_messages(self):
        return self.errors_messages

    def get_result(self):
        return self.get_errors_messages()

    def execute(self, model: PySATModel) -> 'Glucose3ErrorDetection':
        g_r = Glucose3()
        g_r_ctc = Glucose3()
        for clause in model.r_cnf:
            g_r.add_clause(clause)
            g_r_ctc.add_clause(clause)
        for clause in model.ctc_cnf:
            g_r_ctc.add_clause(clause)

        if g_r_ctc.solve():
            dead_features = []
            for feat in model.features:
                if not g_r_ctc.solve(assumptions=[feat]):
                    dead_features.append(model.features.get(feat))
            if dead_features:
                self.errors_messages.append("Dead features: " + str(dead_features))

            false_optional_features = []
            assumption = 1
            for feat in model.features:
                if not g_r_ctc.solve(assumptions=[-feat]) and g_r.solve(assumptions=[-feat]):
                    if g_r.solve(assumptions=[assumption,-feat]):
                        false_optional_features.append(model.features.get(feat))
                    assumption = feat
            if false_optional_features:
                self.errors_messages.append("False optional features: " + str(false_optional_features))

            redundancies = []
            for feat in model.features:
                if not g_r.solve(assumptions=[-feat]):
                    for clause in model.ctc_cnf:
                        if clause[1] == feat:
                            if clause[0]<0:
                                redundancies.append(model.features.get(-clause[0]) + " requires " + model.features.get(feat))
                        if clause[0] == feat:
                            if clause[1]<0:
                                redundancies.append(model.features.get(feat) + " requires " + model.features.get(-clause[1]))

            variables = []
            for clause in model.ctc_cnf:
                if clause[1] in variables:
                    if clause[1] >0:
                        redundancies.append(model.features.get(abs(clause[0])) + " requires " + model.features.get(abs(clause[1])))
                    else:
                        redundancies.append(model.features.get(abs(clause[0])) + " excludes " + model.features.get(abs(clause[1])))
                variables.append(clause[1])

            if redundancies:
                self.errors_messages.append("Redundancies: " + str(redundancies))
        else:
            self.errors_messages.append("The model is void, so haven't any product")

        g_r.delete()
        g_r_ctc.delete()
        return self
