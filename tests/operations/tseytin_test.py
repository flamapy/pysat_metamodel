"""Parity tests: the Tseytin CNF encoding must produce the same analysis results as
the default distributive encoding, while keeping complex constraints compact."""
import os
import tempfile

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations.pysat_configurations import (
    PySATConfigurations,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_configurations_number import (
    PySATConfigurationsNumber,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_satisfiable import PySATSatisfiable


# A model whose cross-tree constraints mix equivalence/implication/negation.
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


def _build(cnf_method):
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(_UVL)
        fm = UVLReader(path).transform()
        return FmToPysat(fm, cnf_method=cnf_method).transform()
    finally:
        os.remove(path)


def _projected_configs(model):
    configs = PySATConfigurations().execute(model).get_result()
    return {frozenset(k for k, v in c.elements.items() if v) for c in configs}


def test_tseytin_matches_distributive_counts_and_configs() -> None:
    distributive = _build('distributive')
    tseytin = _build('tseytin')

    count_d = PySATConfigurationsNumber().execute(distributive).get_result()
    count_t = PySATConfigurationsNumber().execute(tseytin).get_result()
    assert count_d == count_t

    configs_d = _projected_configs(distributive)
    configs_t = _projected_configs(tseytin)
    assert configs_d == configs_t
    # No auxiliary variable ever leaks into a configuration.
    assert all(None not in config for config in configs_t)


def test_tseytin_introduces_auxiliary_variables_kept_out_of_features() -> None:
    tseytin = _build('tseytin')
    assert tseytin.auxiliary_variables  # gates were introduced
    # Auxiliary ids are disjoint from feature ids.
    assert tseytin.auxiliary_variables.isdisjoint(set(tseytin.features.keys()))


def test_tseytin_preserves_satisfiability() -> None:
    assert (
        PySATSatisfiable().execute(_build('distributive')).get_result()
        == PySATSatisfiable().execute(_build('tseytin')).get_result()
    )
