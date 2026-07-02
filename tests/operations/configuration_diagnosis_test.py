"""Configurator-oriented diagnosis: conflict, repair and why-forced explanation."""
import os
import tempfile

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_diagnosis_metamodel.operations import (
    PySATConfigurationConflict,
    PySATConfigurationRepair,
    PySATFeatureExplanation,
)

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


def _sat():
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(_UVL)
        return FmToPysat(UVLReader(path).transform()).transform()
    finally:
        os.remove(path)


def test_conflict_for_inconsistent_decisions():
    op = PySATConfigurationConflict()
    op.set_configuration(Configuration({'A': True, 'B': True}))  # A => !B
    conflict = set(op.execute(_sat()).get_result())
    assert conflict == {('A', True), ('B', True)}


def test_no_conflict_for_consistent_decisions():
    op = PySATConfigurationConflict()
    op.set_configuration(Configuration({'A': True}))
    assert op.execute(_sat()).get_result() == []


def test_repair_retracts_one_conflicting_decision():
    op = PySATConfigurationRepair()
    op.set_configuration(Configuration({'A': True, 'B': True}))
    repair = op.execute(_sat()).get_result()
    # Retracting exactly one of the two clashing decisions restores consistency.
    assert len(repair) == 1
    assert repair[0] in (('A', True), ('B', True))


def test_explanation_of_forced_feature():
    op = PySATFeatureExplanation()
    op.set_configuration(Configuration({'A': True, 'C': True}))  # A active + C => D via C<=>D
    op.set_feature('D')
    op.execute(_sat())
    assert op.get_forced_value() is True
    assert set(op.get_result()) == {('A', True), ('C', True)}


def test_feature_not_forced_has_no_explanation():
    op = PySATFeatureExplanation()
    op.set_configuration(Configuration({'C': True}))  # antecedent (A|B) false -> D free
    op.set_feature('D')
    op.execute(_sat())
    assert op.get_forced_value() is None
    assert op.get_result() == []
