from typing import cast

from pysat.solvers import Solver

from flamapy.core.operations import AtomicSets
from flamapy.core.models import VariabilityModel
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.pysat_backbone import set_phases


class PySATAtomicSets(AtomicSets):
    """The exact atomic sets: the classes of features that have the same value in every
    configuration of the model (the descriptor is the ``AtomicSets`` interface's)."""

    def __init__(self) -> None:
        self.result: list[set[str]] = []

    def get_result(self) -> list[set[str]]:
        return self.result

    def atomic_sets(self) -> list[set[str]]:
        return self.get_result()

    def execute(self, model: VariabilityModel) -> 'PySATAtomicSets':
        self.result = get_atomic_sets(cast(PySATModel, model))
        return self


def get_atomic_sets(model: PySATModel) -> list[set[str]]:
    """The classes of features that every configuration selects together or leaves out
    together, as sets of feature names in the order of the model (a void model has none).

    Two features are in the same class when the formula implies their equivalence. The core
    features form one class and so do the dead features (always deselected together), which
    is what makes the classes usable as units: a model where each class is one variable has
    the same configurations. The tree-only operation of the fm metamodel groups mandatory
    children with their parents; cross-tree constraints can merge those groups, and this
    computes the merged ones.

    Two models with opposite phases split the features into candidate classes (features with
    the same value in both); each round then asks for a model that separates at least one
    candidate class, through an auxiliary variable per (representative, member) pair that
    forces the two apart and one clause over the auxiliaries, guarded by a selector. A model
    refines every class it separates; unsatisfiable means every remaining class is proven, in
    a single call, as in the backbone computation.
    """
    id_to_name = model.features
    features = model.feature_variables()
    solver = Solver(name='glucose3', bootstrap_with=model.get_all_clauses().clauses)
    try:
        set_phases(solver, features)
        if not solver.solve():
            return []
        classes = _split([features], solver.get_model())
        set_phases(solver, [-var for var in features])
        solver.solve()
        classes = _split(classes, solver.get_model())
        classes = _proven_classes(solver, classes, model.top_variable())
    finally:
        solver.delete()
    return [{id_to_name[var] for var in atomic_set}
            for atomic_set in sorted(classes, key=lambda atomic_set: atomic_set[0])]


def _split(classes: list[list[int]], assignment: list[int]) -> list[list[int]]:
    """Refine the classes by the values the assignment gives their variables."""
    true_variables = {lit for lit in assignment if lit > 0}
    refined = []
    for atomic_set in classes:
        selected = [var for var in atomic_set if var in true_variables]
        deselected = [var for var in atomic_set if var not in true_variables]
        refined += [part for part in (selected, deselected) if part]
    return refined


def _proven_classes(solver: Solver, classes: list[list[int]], top_variable: int) -> list[list[int]]:
    """The classes refined until the solver proves that every member of each class takes the
    value of its first member in every model; `solver` holds the formula."""
    proven = [atomic_set for atomic_set in classes if len(atomic_set) == 1]
    pending = [atomic_set for atomic_set in classes if len(atomic_set) > 1]
    differs: dict[tuple[int, int], int] = {}   # (representative, member) -> auxiliary variable
    while pending:
        auxiliaries = []
        phases = []
        for atomic_set in pending:
            representative = atomic_set[0]
            for member in atomic_set[1:]:
                auxiliary = differs.get((representative, member))
                if auxiliary is None:
                    top_variable += 1
                    auxiliary = differs[(representative, member)] = top_variable
                    # auxiliary -> representative and member take different values
                    solver.add_clause([-auxiliary, representative, member])
                    solver.add_clause([-auxiliary, -representative, -member])
                auxiliaries.append(auxiliary)
                phases += [auxiliary, representative, -member]
        top_variable += 1
        selector = top_variable
        solver.add_clause([*auxiliaries, selector])
        set_phases(solver, phases)
        if not solver.solve(assumptions=[-selector]):
            return proven + pending
        # read the model before adding a clause: some solvers (CaDiCaL) drop it on add_clause
        refined = _split(pending, solver.get_model())
        solver.add_clause([selector])  # retire the clause of this round
        proven += [atomic_set for atomic_set in refined if len(atomic_set) == 1]
        pending = [atomic_set for atomic_set in refined if len(atomic_set) > 1]
    return proven
