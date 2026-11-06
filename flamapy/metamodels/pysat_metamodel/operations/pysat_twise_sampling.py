import itertools
import random
import threading
from typing import Any, Iterator, Optional, cast

from pysat.solvers import Solver

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor, Input
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.pysat_backbone import get_backbone, set_phases

# Models found before the greedy covering starts: the two extreme models (every feature
# preferred selected, then deselected) and this many random-phase models. Together they realize
# most of the satisfiable pairs for free.
RANDOM_SEED_MODELS = 8


class PySATTWiseSampling(Operation):
    """t-wise (combinatorial) sampling: a set of valid configurations that covers every
    satisfiable combination of ``t`` feature selections.

    For ``t = 2`` this yields a pairwise covering sample, built without enumerating the
    combinations (see `pairwise_cover`). For other ``t`` the satisfiable combinations are
    enumerated first and the sample is built greedily: each configuration is grown to cover as
    many still-uncovered feature combinations as the constraints allow.
    """

    facade = OperationDescriptor(
        doc=(
            'Returns a t-wise (combinatorial) sample: a set of valid configurations that\n'
            'covers every satisfiable combination of ``t`` feature selections (pairwise for\n'
            '``t = 2``).\n'
            '\n'
            '``backend`` selects the analysis plugin; only "sat" implements t-wise\n'
            'sampling.'
        ),
        returns='Union[None, List[Configuration]]',
        name='t_wise_sampling', operation='PySATTWiseSampling', default_backend='sat',
        selectable_backend=True,
        inputs=(Input('t', int, default=2, setter='set_t'),),
    )

    def __init__(self, t: int = 2) -> None:
        self.t = t
        self.result: list[Configuration] = []

    def set_t(self, t: int) -> None:
        self.t = t

    def get_sample(self) -> list[Configuration]:
        return self.result

    def get_result(self) -> list[Configuration]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATTWiseSampling':
        sat_model = cast(PySATModel, model)
        self.result = _twise_sample(sat_model, self.t)
        return self


def _satisfiable_targets(solver: Solver, feature_vars: list[int], t: int) -> list[tuple[int, ...]]:
    """Every satisfiable combination of ``t`` feature variables with each sign pattern, by one
    solver call per combination (quadratic in the features for t = 2: see `pairwise_cover`)."""
    targets: list[tuple[int, ...]] = []
    for combination in itertools.combinations(feature_vars, t):
        for signs in itertools.product((1, -1), repeat=t):
            literals = tuple(sign * var for sign, var in zip(signs, combination))
            if solver.solve(assumptions=list(literals)):
                targets.append(literals)
    return targets


def satisfiable_targets(model: PySATModel, t: int) -> list[tuple[int, ...]]:
    """The satisfiable combinations of ``t`` feature literals (over distinct variables)."""
    if t == 2:  # noqa: PLR2004
        return pairwise_cover(model)[1].pairs()
    solver = Solver(name='glucose3', bootstrap_with=list(model.get_all_clauses().clauses))
    try:
        return _satisfiable_targets(solver, model.feature_variables(), t)
    finally:
        solver.delete()


def _twise_sample(model: PySATModel, t: int, seed: Optional[int] = None,
                  interrupt_event: Optional[threading.Event] = None) -> list[Configuration]:
    if t == 2:  # noqa: PLR2004
        assignments = pairwise_sample(model, seed, interrupt_event)
        return [_to_configuration(model, assignment) for assignment in assignments]
    solver = Solver(name='glucose3', bootstrap_with=list(model.get_all_clauses().clauses))
    try:
        uncovered = _satisfiable_targets(solver, model.feature_variables(), t)
        if seed is not None:
            random.Random(seed).shuffle(uncovered)
        return _greedy_cover(solver, model, uncovered, interrupt_event)
    finally:
        solver.delete()


def _greedy_cover(solver: Solver, model: PySATModel, uncovered: list[tuple[int, ...]],
                  interrupt_event: Optional[threading.Event] = None) -> list[Configuration]:
    """Grow one configuration at a time from the first uncovered target, merging every other
    target that stays jointly satisfiable, until every target is covered."""
    configurations: list[Configuration] = []
    while uncovered:
        if interrupt_event is not None and interrupt_event.is_set():
            break  # cooperative cancellation: return the partial sample
        current: set[int] = set(uncovered[0])
        for target in uncovered[1:]:
            if any(-literal in current for literal in target):
                continue
            tentative = current | set(target)
            if solver.solve(assumptions=list(tentative)):
                current = tentative
        solver.solve(assumptions=list(current))
        assignment = solver.get_model() or []
        configurations.append(_to_configuration(model, assignment))
        satisfied = set(assignment)
        uncovered = [tg for tg in uncovered if not set(tg).issubset(satisfied)]
    return configurations


class PairCoverage:
    """Which pairs of feature literals are covered, impossible or unsatisfiable, as bitsets.

    The literal of the i-th feature variable has index 2i (negative) or 2i + 1 (positive).
    ``covered[k]`` has bit m set when the literals k and m were selected together in some
    configuration found so far; marking a configuration costs one big-integer OR per feature,
    and the uncovered partners of a literal are one AND-NOT away. ``impossible`` holds the
    literals no configuration selects (the complement of the backbone); ``unsatisfiable[k]``
    the partners proven incompatible with k on their own.
    """

    def __init__(self, feature_vars: list[int]) -> None:
        self.feature_vars = list(feature_vars)
        self._position = {var: index for index, var in enumerate(self.feature_vars)}
        self.size = 2 * len(self.feature_vars)
        self._all = (1 << self.size) - 1
        self.covered = [0] * self.size
        self.unsatisfiable = [0] * self.size
        self.impossible = 0

    def index(self, literal: int) -> int:
        return 2 * self._position[abs(literal)] + (1 if literal > 0 else 0)

    def literal(self, index: int) -> int:
        var = self.feature_vars[index // 2]
        return var if index % 2 else -var

    def indices(self, assignment: list[int]) -> list[int]:
        """The literal indices of the feature literals of a solver model."""
        return [self.index(literal) for literal in assignment if abs(literal) in self._position]

    def mark(self, assignment: list[int]) -> list[int]:
        """Record every pair the assignment realizes; returns its literal indices."""
        indices = self.indices(assignment)
        bits = 0
        for index in indices:
            bits |= 1 << index
        for index in indices:
            self.covered[index] |= bits
        return indices

    def uncovered_partners(self, index: int, excluded: int = 0) -> int:
        """The literals of other variables that index could still pair with."""
        own_variable = 3 << (2 * (index // 2))
        return (self._all & ~self.covered[index] & ~self.impossible & ~self.unsatisfiable[index]
                & ~own_variable & ~excluded)

    def pairs(self) -> list[tuple[int, ...]]:
        """Every covered pair as (literal of the lower variable, literal of the higher one)."""
        result: list[tuple[int, ...]] = []
        for index in range(self.size):
            higher = self.covered[index] >> (2 * (index // 2) + 2) << (2 * (index // 2) + 2)
            for partner in _bits(higher):
                result.append((self.literal(index), self.literal(partner)))
        return result

    def total(self) -> int:
        """The number of covered pairs (over distinct variables)."""
        return sum((bits & ~(3 << (2 * (index // 2)))).bit_count()
                   for index, bits in enumerate(self.covered)) // 2


def _bits(value: int) -> Iterator[int]:
    while value:
        lowest = value & -value
        yield lowest.bit_length() - 1
        value ^= lowest


def pairwise_cover(model: PySATModel, seed: Optional[int] = None,
                   interrupt_event: Optional[threading.Event] = None
                   ) -> tuple[list[list[int]], PairCoverage]:
    """Valid configurations that together realize every satisfiable pair of feature literals,
    and the pair bookkeeping (whose covered set is then exactly the satisfiable pairs).

    No pair is enumerated up front: the backbone rules out the pairs with an impossible literal,
    seed models (the two extremes and random-phase ones) realize most pairs, and the greedy loop
    only tests the pairs no model has realized, by unit propagation before a full solve, taking
    every model the solver returns as coverage. A pair that fails on its own is unsatisfiable
    and never tried again. ``seed`` permutes the literal order and the random phases, which
    makes the result reproducible per seed and different across seeds.
    """
    solver = Solver(name='glucose3', bootstrap_with=list(model.get_all_clauses().clauses))
    try:
        coverage = PairCoverage(model.feature_variables())
        if not solver.solve():
            return [], coverage
        backbone = get_backbone(model)
        for name in backbone['core']:
            coverage.impossible |= 1 << coverage.index(-model.variables[name])
        for name in backbone['dead']:
            coverage.impossible |= 1 << coverage.index(model.variables[name])
        rng = random.Random(0 if seed is None else seed)
        features = coverage.feature_vars
        assignments: list[list[int]] = []
        phase_choices = [features, [-var for var in features]]
        phase_choices += [[var if rng.random() < 0.5 else -var for var in features]  # noqa: PLR2004
                          for _ in range(RANDOM_SEED_MODELS)]
        for phases in phase_choices:
            set_phases(solver, phases)
            solver.solve()
            assignment = solver.get_model()
            coverage.mark(assignment)
            assignments.append(assignment)
        order = list(range(coverage.size))
        if seed is not None:
            rng.shuffle(order)
        while interrupt_event is None or not interrupt_event.is_set():
            assignment, progress = _grow_configuration(solver, coverage, order)
            if assignment is not None:
                # Only kept models count as coverage: the pairs of the intermediate models of
                # the growth that its final model does not realize stay uncovered.
                coverage.mark(assignment)
                assignments.append(assignment)
            if not progress:
                break
        return assignments, coverage
    finally:
        solver.delete()


class _Growth:
    """One configuration being grown: the literals fixed so far and the last model found,
    which realizes every fixed pair."""

    def __init__(self, solver: Solver, coverage: PairCoverage) -> None:
        self.solver = solver
        self.coverage = coverage
        self.current: list[int] = []
        self.fixed = 0        # literal indices fixed in the configuration
        self.conflict = 0     # literal indices whose variable is fixed with the other sign
        self.model: Optional[list[int]] = None
        self.model_bits = 0   # literal indices of the last model: its pairs need no test
        self.progress = False  # a pair fixed, or proven unsatisfiable on its own

    def realized(self, index: int, partner: int) -> bool:
        return bool((self.model_bits >> index) & 1 and (self.model_bits >> partner) & 1)

    def try_pair(self, index: int, partner: int) -> None:
        """Fix the pair if it is satisfiable with the fixed literals (unit propagation first,
        then a full solve); a pair unsatisfiable on its own is recorded as such."""
        coverage = self.coverage
        assumptions = [*self.current, coverage.literal(index), coverage.literal(partner)]
        satisfiable, _ = self.solver.propagate(assumptions=assumptions)
        if satisfiable:
            satisfiable = self.solver.solve(assumptions=assumptions)
        if satisfiable:
            self.model = self.solver.get_model()
            self.model_bits = 0
            for literal_index in coverage.indices(self.model):
                self.model_bits |= 1 << literal_index
            for literal_index in (index, partner):
                if not (self.fixed >> literal_index) & 1:
                    self.current.append(coverage.literal(literal_index))
                    self.fixed |= 1 << literal_index
                    self.conflict |= 1 << (literal_index ^ 1)
            self.progress = True
        elif not self.current:
            coverage.unsatisfiable[index] |= 1 << partner
            coverage.unsatisfiable[partner] |= 1 << index
            self.progress = True


def _grow_configuration(solver: Solver, coverage: PairCoverage,
                        order: list[int]) -> tuple[Optional[list[int]], bool]:
    """One greedy configuration: fix pairs that are still uncovered while they stay jointly
    satisfiable. Returns the last model found (None if none) and whether anything changed."""
    growth = _Growth(solver, coverage)
    for index in order:
        if (coverage.impossible >> index) & 1 or (growth.conflict >> index) & 1:
            continue
        for partner in _bits(coverage.uncovered_partners(index, growth.conflict)):
            if not growth.realized(index, partner):
                growth.try_pair(index, partner)
    return growth.model, growth.progress


def pairwise_sample(model: PySATModel, seed: Optional[int] = None,
                    interrupt_event: Optional[threading.Event] = None) -> list[list[int]]:
    """A pairwise covering sample: the configurations of `pairwise_cover` reduced by a greedy
    set cover, which drops the seed and intermediate models the later ones made redundant."""
    assignments, coverage = pairwise_cover(model, seed, interrupt_event)
    return _reduce(assignments, coverage)


def _reduce(assignments: list[list[int]], coverage: PairCoverage) -> list[list[int]]:
    """Greedy set cover of the pairs the assignments realize, over the assignments."""
    candidates = []
    for assignment in assignments:
        indices = coverage.indices(assignment)
        bits = 0
        for index in indices:
            bits |= 1 << index
        candidates.append((bits, indices))
    uncovered = [0] * coverage.size
    for bits, indices in candidates:
        for index in indices:
            uncovered[index] |= bits
    chosen: list[int] = []
    remaining = set(range(len(candidates)))
    while remaining:
        best = max(remaining, key=lambda position: sum(
            (candidates[position][0] & uncovered[index]).bit_count()
            for index in candidates[position][1]))
        bits, indices = candidates[best]
        if not any(bits & uncovered[index] for index in indices):
            break
        chosen.append(best)
        remaining.discard(best)
        for index in indices:
            uncovered[index] &= ~bits
    return [assignments[position] for position in sorted(chosen)]


def _to_configuration(model: PySATModel, assignment: list[int]) -> Configuration:
    elements: dict[Any, Any] = {}
    for literal in assignment:
        if literal > 0:
            name = model.features.get(literal)
            if name is not None:  # skip auxiliary variables
                elements[name] = True
    return Configuration(elements)
