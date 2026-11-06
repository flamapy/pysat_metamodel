from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATBackbone(Operation):
    facade = OperationDescriptor(
        doc=(
            'Returns the backbone of the feature model: the set of features that must\n'
            'always be selected (core) and those that must never be selected (dead) across\n'
            "all valid configurations, grouped under 'core' and 'dead' keys."
        ),
        returns='Union[None, Dict[str, List[Any]]]',
        name='backbone', operation='PySATBackbone', default_backend='sat'
    )

    def __init__(self) -> None:
        self._result: dict[str, list[Any]] = {"core": [], "dead": []}


    def get_backbone(self) -> dict[str, list[Any]]:
        return self.get_result()

    def get_result(self) -> dict[str, list[Any]]:
        return self._result

    def execute(self, model: VariabilityModel) -> 'PySATBackbone':
        sat_model = cast(PySATModel, model)
        self._result = get_backbone(sat_model)
        return self


def set_phases(solver: Solver, literals: list[int]) -> None:
    """Ask the solver to try these literals first (a heuristic: results never depend on it)."""
    try:
        solver.set_phases(literals)
    except NotImplementedError:  # a PySAT solver without phase selection
        pass


def get_backbone(model: PySATModel) -> dict[str, list[Any]]:
    """Core and dead features: the backbone of the formula restricted to the feature variables.

    The candidates are the feature literals of a first model; every other model prunes the
    candidates it falsifies. Each round asks for a model that falsifies at least one candidate
    (the clause -c1 v ... v -ck, guarded by a selector so that it can be retired); when that is
    unsatisfiable, every remaining candidate belongs to the backbone, in a single call
    (Marques-Silva, Janota and Lynce, 2010, the iterative algorithm with the complement of the
    backbone estimate). Two preliminary models, with every feature preferred selected and then
    deselected, and solver phases set against the candidates make each model prune as many
    candidates as possible; FeatureIDE's core/dead analysis uses the same extreme models. With
    phase saving alone (the solver's default) consecutive models differ in a handful of literals
    and large models need one call per feature.
    """
    id_to_name = model.features
    features = model.feature_variables()
    solver = Solver(name='glucose3', bootstrap_with=model.get_all_clauses().clauses)
    try:
        set_phases(solver, features)
        if not solver.solve():
            return {"core": [], "dead": list(id_to_name.values())}
        candidates = {lit for lit in solver.get_model() if abs(lit) in id_to_name}
        set_phases(solver, [-var for var in features])
        solver.solve()
        candidates &= set(solver.get_model())
        backbone = _backbone_literals(solver, candidates, model.top_variable())
    finally:
        solver.delete()
    return {"core": [id_to_name[lit] for lit in sorted(backbone) if lit > 0],
            "dead": [id_to_name[-lit] for lit in sorted(backbone, reverse=True) if lit < 0]}


def _backbone_literals(solver: Solver, candidates: set[int], top_variable: int) -> set[int]:
    """The candidates that hold in every model; `solver` holds the formula and keeps its clauses."""
    while candidates:
        top_variable += 1
        selector = top_variable
        solver.add_clause([-lit for lit in candidates] + [selector])
        set_phases(solver, [-lit for lit in candidates])
        if not solver.solve(assumptions=[-selector]):
            return candidates
        # read the model before adding a clause: some solvers (CaDiCaL) drop it on add_clause
        candidates &= set(solver.get_model())
        solver.add_clause([selector])  # retire the clause of this round
    return candidates
