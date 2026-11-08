from itertools import chain
from typing import Iterable, Iterator, Optional

from pysat.formula import CNF
from pysat.solvers import Solver

from flamapy.core.exceptions import FlamaException
from flamapy.core.models import VariabilityModel


class PySATModel(VariabilityModel):
    @staticmethod
    def get_extension() -> str:
        return 'pysat'

    def __init__(self) -> None:
        self._cnf = CNF()
        self.variables: dict[str, int] = {}  # feature's name -> id
        self.features: dict[int, str] = {}  # id -> feature's name
        # Auxiliary (Tseytin) variable ids that are not features. They must be excluded
        # from feature enumeration/counting; models over the features are unaffected.
        self.auxiliary_variables: set[int] = set()
        # The ClauseSet encoding the clauses come from ('auto', 'distributive' or 'tseytin'),
        # or None when flamapy did not encode them (e.g. a model read from DIMACS). Operations
        # that re-encode the feature model use it to keep the same encoding.
        self.cnf_method: Optional[str] = None
        self.original_model: VariabilityModel

    def add_clause(self, clause: list[int]) -> None:
        self._cnf.append(clause)

    def get_variable(self, key: str) -> int:
        if key not in self.variables:
            raise FlamaException(f'Feature {key} not found')
        return self.variables[key]

    def get_all_clauses(self) -> CNF:
        return self._cnf

    # ---- feature projection helpers -------------------------------------------------------
    # With cnf_method 'tseytin'/'auto' the CNF also contains auxiliary variables. Results are
    # always reported over the features only; these helpers keep that in one place.

    def is_feature(self, variable: int) -> bool:
        """Whether a variable (or literal) is a feature, i.e. not an auxiliary variable."""
        return abs(variable) in self.features

    def is_auxiliary(self, variable: int) -> bool:
        """Whether a variable (or literal) is an auxiliary (Tseytin) variable."""
        return abs(variable) in self.auxiliary_variables

    def feature_variables(self) -> list[int]:
        """The ids of the feature variables, in increasing order."""
        return sorted(self.features)

    def top_variable(self) -> int:
        """The highest variable id used by the encoding (features and auxiliary variables).

        New variables (e.g. diagnosis assumption selectors) must start above it.
        """
        return max(chain(self.features, self.variables.values(), self.auxiliary_variables),
                   default=0)

    def selected_features(self, assignment: Iterable[int]) -> list[str]:
        """Names of the features set to true in a solver assignment, in assignment order.

        Auxiliary variables are skipped.
        """
        return [self.features[literal] for literal in assignment
                if literal > 0 and literal in self.features]

    def enum_feature_models(self, solver: Solver,
                            assumptions: Iterable[int] = ()) -> Iterator[list[int]]:
        """Enumerate the solver's models, one per distinct assignment of the features.

        ``solver`` must already hold this model's clauses. Without auxiliary variables this is
        exactly ``solver.enum_models``. With them, each model found is blocked on its feature
        literals only, so models that differ only in auxiliary variables count once. (The
        Tseytin gates of ClauseSet are biconditionals, which already makes the auxiliary
        assignment unique, but the operations do not have to rely on that.) Like
        ``enum_models``, this adds the blocking clauses to ``solver``.
        """
        assumptions = list(assumptions)
        if not self.auxiliary_variables:
            yield from solver.enum_models(assumptions=assumptions)
            return
        feature_variables = self.feature_variables()
        while solver.solve(assumptions=assumptions):
            model = solver.get_model()
            yield model
            true_literals = set(model)
            solver.add_clause([-variable if variable in true_literals else variable
                               for variable in feature_variables])

    def __eq__(self, other: object) -> bool:
        if other is None or not isinstance(other, PySATModel):
            return False
        return set(self.get_all_clauses().clauses) == set(other.get_all_clauses().clauses)

    def __hash__(self) -> int:
        clause_tuples = (tuple(clause) for clause in self.get_all_clauses().clauses)
        return hash(frozenset(clause_tuples))
