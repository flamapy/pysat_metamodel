import logging
from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.operations import FalseOptionalFeatures
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.pysat_backbone import set_phases
from flamapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from flamapy.core.models import VariabilityModel, VariabilityElement
from flamapy.core.exceptions import FlamaException


LOGGER = logging.getLogger('PySATFalseOptionalFeatures')


class PySATFalseOptionalFeatures(FalseOptionalFeatures):

    def __init__(self) -> None:
        self.result: list[Any] = []
        self.solver = Solver(name='glucose3')

    def execute(self, model: VariabilityModel) -> 'PySATFalseOptionalFeatures':
        sat_model = cast(PySATModel, model)
        self.result = self._get_false_optional_features(sat_model)
        return self

    def get_false_optional_features(self) -> list[VariabilityElement]:
        return self.get_result()

    def get_result(self) -> list[Any]:
        return self.result

    def _get_false_optional_features(self, sat_model: PySATModel) -> list[Any]:
        original_model = getattr(sat_model, 'original_model', None)
        if original_model is None:
            raise FlamaException("The transformation didn't attach the source model, "
                                 "which is required for this operation.")
        feature_model = cast(FeatureModel, original_model)

        real_optional_features = [f for f in feature_model.get_features()
                                  if not f.is_root() and not f.is_mandatory()]

        # (parent variable, feature variable) -> feature name, in the order of the model
        pairs: dict[tuple[int, int], str] = {}
        for feature in real_optional_features:
            variable = sat_model.variables.get(feature.name)
            parent_feature = feature.get_parent()
            if parent_feature is not None:
                parent_variable = sat_model.variables.get(parent_feature.name)
                assert variable is not None
                assert parent_variable is not None
                pairs[(parent_variable, variable)] = feature.name

        for clause in sat_model.get_all_clauses():
            self.solver.add_clause(clause)
        implied = implied_pairs(self.solver, set(pairs), sat_model.top_variable())
        self.solver.delete()
        return [name for pair, name in pairs.items() if pair in implied]


def implied_pairs(solver: Solver, pairs: set[tuple[int, int]],
                  top_variable: int) -> set[tuple[int, int]]:
    """The pairs (parent, feature) such that the formula in `solver` with the parent selected
    never leaves the feature deselected (on an unsatisfiable formula, every pair).

    A model with the parent selected and the feature deselected refutes a pair. Two preliminary
    models, with every variable of the pairs preferred selected and then deselected, refute most
    pairs at once. The remaining pairs are tested together: an auxiliary variable a_i -> (parent_i
    and not feature_i) per pair and the clause a_1 v ... v a_k (guarded by a selector) ask for a
    model that refutes at least one of them; when that is unsatisfiable, every remaining pair is
    implied. Phases are set to refute as many pairs as possible in each model.
    """
    pending = set(pairs)
    variables = sorted({var for pair in pending for var in pair})

    def prune() -> None:
        model = set(solver.get_model())
        pending.difference_update({(parent, feature) for parent, feature in pending
                                   if parent in model and -feature in model})

    set_phases(solver, variables)
    if not solver.solve():
        return pending
    prune()
    set_phases(solver, [-var for var in variables])
    solver.solve()
    prune()

    auxiliary: dict[tuple[int, int], int] = {}
    for parent, feature in pending:
        top_variable += 1
        auxiliary[(parent, feature)] = top_variable
        solver.add_clause([-top_variable, parent])
        solver.add_clause([-top_variable, -feature])
    while pending:
        top_variable += 1
        selector = top_variable
        solver.add_clause([auxiliary[pair] for pair in pending] + [selector])
        set_phases(solver, [auxiliary[pair] for pair in pending]
                   + [parent for parent, _ in pending] + [-feature for _, feature in pending])
        if not solver.solve(assumptions=[-selector]):
            break
        prune()  # reads the model: before adding a clause, which makes CaDiCaL drop it
        solver.add_clause([selector])  # retire the clause of this round
    return pending
