"""MaxSAT-based optimal configuration on the SAT backend, checked against z3."""
import os
import tempfile

import pytest

from flamapy.core.operations import OptimizationGoal
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations.pysat_attribute_optimization import (
    PySATAttributeOptimization,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_minimum_configuration import (
    PySATMinimumConfiguration,
)

_UVL = """features
    Root {abstract}
        optional
            A {Cost 3}
            B {Cost 5}
            C {Cost 2}
constraints
    A | B
"""


def _sat_model():
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(_UVL)
        return FmToPysat(UVLReader(path).transform()).transform()
    finally:
        os.remove(path)


def _selected(configuration):
    return sorted(name for name, value in configuration.elements.items() if value)


@pytest.mark.parametrize('goal, expected_cost, expected_features', [
    (OptimizationGoal.MINIMIZE, 3.0, ['A', 'Root']),
    (OptimizationGoal.MAXIMIZE, 10.0, ['A', 'B', 'C', 'Root']),
])
def test_attribute_optimization(goal, expected_cost, expected_features):
    op = PySATAttributeOptimization()
    op.set_attributes({'Cost': goal})
    op.execute(_sat_model())
    assert op.get_optimum() == {'Cost': expected_cost}
    assert _selected(op.get_result()[0]) == expected_features


def test_multi_attribute_is_rejected():
    op = PySATAttributeOptimization()
    op.set_attributes({'Cost': OptimizationGoal.MINIMIZE, 'Weight': OptimizationGoal.MINIMIZE})
    with pytest.raises(Exception):
        op.execute(_sat_model())


def test_minimum_configuration_selects_one_optional_feature():
    result = PySATMinimumConfiguration().execute(_sat_model()).get_result()
    selected = set(_selected(result))
    # Root plus exactly one of A/B satisfies "A | B" with the fewest features.
    assert 'Root' in selected
    assert len(selected) == 2
    assert len(selected & {'A', 'B'}) == 1
    assert 'C' not in selected


def test_matches_z3_optimum():
    z3 = pytest.importorskip('flamapy.metamodels.z3_metamodel.operations.z3_attribute_optimization')
    from flamapy.metamodels.z3_metamodel.transformations import FmToZ3
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(_UVL)
        fm = UVLReader(path).transform()
    finally:
        os.remove(path)
    for goal in (OptimizationGoal.MINIMIZE, OptimizationGoal.MAXIMIZE):
        pysat_op = PySATAttributeOptimization()
        pysat_op.set_attributes({'Cost': goal})
        pysat_op.execute(FmToPysat(fm).transform())
        z3_op = z3.Z3AttributeOptimization()
        z3_op.set_attributes({'Cost': goal})
        z3_op.execute(FmToZ3(fm).transform())
        z3_values = {values['Cost'] for _config, values in z3_op.get_result()}
        assert pysat_op.get_optimum()['Cost'] in z3_values
