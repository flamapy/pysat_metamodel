"""The pairwise cover realizes exactly the satisfiable pairs the exhaustive enumeration finds,
the reduced sample still covers them all, and seeds make covering arrays reproducible."""
import os
import tempfile

from pysat.solvers import Solver

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations.pysat_twise_sampling import (
    PySATTWiseSampling,
    _satisfiable_targets,
    pairwise_cover,
    pairwise_sample,
    satisfiable_targets,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_testing import (
    PySATCoverage,
    PySATCoveringArray,
)

MODEL = '''features
    Root
        mandatory
            Core
            Screen
                alternative
                    Analog
                    HighRes
                    EInk
        optional
            Connector
                or
                    USB
                    Wireless
                    Bluetooth
            Camera
            GPS
            Unreachable
            Always
            NeedsParent
                optional
                    Child
constraints
    Camera => HighRes
    Unreachable => !Root
    Core => Always
    NeedsParent => Child
    GPS => Connector
'''

VOID = '''features
    Root
        optional
            A
constraints
    !Root
'''


def _sat_model(uvl):
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(uvl)
        return FmToPysat(UVLReader(path).transform()).transform()
    finally:
        os.remove(path)


def _pairs(targets):
    return {tuple(sorted(target, key=abs)) for target in targets}


def test_cover_realizes_exactly_the_satisfiable_pairs():
    model = _sat_model(MODEL)
    solver = Solver(name='glucose3', bootstrap_with=list(model.get_all_clauses().clauses))
    try:
        exhaustive = _pairs(_satisfiable_targets(solver, model.feature_variables(), 2))
    finally:
        solver.delete()
    assignments, coverage = pairwise_cover(model)
    assert _pairs(coverage.pairs()) == exhaustive
    assert coverage.total() == len(exhaustive)
    assert _pairs(satisfiable_targets(model, 2)) == exhaustive
    # a pair with a dead feature selected or a core feature deselected is impossible
    dead, core = model.variables['Unreachable'], model.variables['Always']
    assert (coverage.impossible >> coverage.index(dead)) & 1
    assert (coverage.impossible >> coverage.index(-core)) & 1
    assert all(abs(literal) in model.features for assignment in assignments
               for literal in assignment if abs(literal) in model.features)


def test_reduced_sample_keeps_full_coverage_with_fewer_configurations():
    model = _sat_model(MODEL)
    assignments, _ = pairwise_cover(model)
    sample = pairwise_sample(model)
    assert 0 < len(sample) < len(assignments)
    configurations = PySATTWiseSampling(t=2).execute(model).get_sample()
    assert len(configurations) == len(sample)
    coverage = PySATCoverage(t=2)
    coverage.set_configurations(configurations)
    assert coverage.execute(model).get_result() == 1.0


def test_covering_array_is_reproducible_per_seed_and_complete():
    model = _sat_model(MODEL)
    first = PySATCoveringArray(t=2, seed=3).execute(model).get_result()
    second = PySATCoveringArray(t=2, seed=3).execute(model).get_result()
    assert [c.elements for c in first] == [c.elements for c in second]
    coverage = PySATCoverage(t=2)
    coverage.set_configurations(PySATCoveringArray(t=2, seed=11).execute(model).get_result())
    assert coverage.execute(model).get_result() == 1.0


def test_void_model_has_no_pairs_and_an_empty_sample():
    model = _sat_model(VOID)
    assignments, coverage = pairwise_cover(model)
    assert assignments == [] and coverage.total() == 0
    assert PySATTWiseSampling(t=2).execute(model).get_sample() == []
    assert satisfiable_targets(model, 2) == []
