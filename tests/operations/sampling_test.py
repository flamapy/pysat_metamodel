"""t-wise sampling coverage and the partial-configuration sampling fix."""
import itertools
import os
import tempfile

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations.pysat_sampling import PySATSampling
from flamapy.metamodels.pysat_metamodel.operations.pysat_twise_sampling import (
    PySATTWiseSampling,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_satisfiable_configuration import (
    PySATSatisfiableConfiguration,
)
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration

_UVL = """features
    Root {abstract}
        optional
            A
            B
            C
            D
constraints
    (A | B) => (C <=> D)
    A => !B
"""


def _fm():
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(_UVL)
        return UVLReader(path).transform()
    finally:
        os.remove(path)


def _sat():
    return FmToPysat(_fm()).transform()


def _selected(configuration):
    return {name for name, value in configuration.elements.items() if value}


def _is_valid(fm, sat_model, selected):
    elements = {feature.name: (feature.name in selected) for feature in fm.get_features()}
    configuration = Configuration(elements)
    configuration.set_full(True)
    op = PySATSatisfiableConfiguration()
    op.set_configuration(configuration)
    return op.execute(sat_model).get_result()


def _pair_satisfiable(sat_model, f1, v1, f2, v2):
    from pysat.solvers import Solver
    variables = sat_model.variables
    solver = Solver(name='glucose3', bootstrap_with=list(sat_model.get_all_clauses().clauses))
    assumptions = [variables[f1] if v1 else -variables[f1],
                   variables[f2] if v2 else -variables[f2]]
    result = solver.solve(assumptions=assumptions)
    solver.delete()
    return result


def test_pairwise_sampling_covers_all_valid_pairs():
    fm = _fm()
    sat_model = FmToPysat(fm).transform()
    sample = PySATTWiseSampling(t=2).execute(sat_model).get_sample()

    # Every sampled configuration is valid.
    for configuration in sample:
        assert _is_valid(fm, FmToPysat(fm).transform(), _selected(configuration))

    # Every *satisfiable* (feature, value) pair must be covered by some configuration;
    # unsatisfiable pairs (e.g. A & B, since A => !B) are legitimately absent.
    features = ['A', 'B', 'C', 'D']
    selected_sets = [_selected(c) for c in sample]
    for f1, f2 in itertools.combinations(features, 2):
        for v1, v2 in itertools.product((True, False), repeat=2):
            covered = any((f1 in s) == v1 and (f2 in s) == v2 for s in selected_sets)
            if not covered:
                assert not _pair_satisfiable(sat_model, f1, v1, f2, v2)


def test_sampling_honours_partial_configuration():
    op = PySATSampling()
    op.set_sample_size(5)
    op.set_partial_configuration(Configuration({'A': True}))
    sample = op.execute(_sat()).get_sample()
    assert sample
    for configuration in sample:
        selected = _selected(configuration)
        assert 'A' in selected      # fixed feature respected
        assert 'B' not in selected  # A => !B forces B out
