"""The CNF method (distributive / tseytin / auto) must not change any operation result.

Tseytin introduces auxiliary variables. These tests cover the places where they could leak
into results (Filter products), be confused with other variables (diagnosis assumption
selectors) or be dropped (explanations re-encoding the model), plus the PySATModel
projection helpers the operations use.
"""
import os
import tempfile

import pytest

from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.operations import (
    PySATConfigurations,
    PySATConfigurationsNumber,
    PySATFilter,
    PySATSampling,
)
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_diagnosis_metamodel.operations import (
    PySATConflict,
    PySATDiagnosis,
    PySATExplainVoidModel,
)
from flamapy.metamodels.pysat_diagnosis_metamodel.operations.pysat_explanations import (
    _prepared_model,
)
from flamapy.metamodels.pysat_diagnosis_metamodel.transformations import FmToDiagPysat

METHODS = ('distributive', 'tseytin', 'auto')

# The first constraint is wide enough for 'auto' to choose Tseytin.
_UVL = """features
    Root {abstract}
        optional
            A
            B
            C
            D
            E
            F
constraints
    (A & B & C) | (D & E & F) | (B & E & F)
    A => !D
"""

# A void model: the diagnosis results depend on telling assumption selectors and
# auxiliary variables apart.
_VOID_UVL = """features
    Root
        mandatory
            A
        optional
            B
            C
constraints
    A => (B & C) | (!B & !C)
    A => B
    !C | !A
    B => C
"""


def _fm(uvl):
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(uvl)
        return UVLReader(path).transform()
    finally:
        os.remove(path)


def _configs(result):
    return {frozenset(k for k, v in c.elements.items() if v) for c in result}


@pytest.mark.parametrize('method', METHODS)
def test_cnf_method_is_recorded(method):
    fm = _fm(_UVL)
    assert FmToPysat(fm, cnf_method=method).transform().cnf_method == method
    assert FmToDiagPysat(fm, cnf_method=method).transform().cnf_method == method


def test_auto_and_tseytin_introduce_auxiliary_variables():
    fm = _fm(_UVL)
    assert not FmToPysat(fm, cnf_method='distributive').transform().auxiliary_variables
    assert FmToPysat(fm, cnf_method='tseytin').transform().auxiliary_variables
    assert FmToPysat(fm, cnf_method='auto').transform().auxiliary_variables


def test_projection_helpers():
    model = FmToPysat(_fm(_UVL), cnf_method='tseytin').transform()
    aux = sorted(model.auxiliary_variables)
    features = model.feature_variables()
    assert features == sorted(model.features)
    assert all(model.is_feature(v) and not model.is_auxiliary(v) for v in features)
    assert all(model.is_auxiliary(v) and not model.is_feature(-v) for v in aux)
    assert model.top_variable() == max(features + aux)
    assignment = [features[0], -features[1], aux[0], -aux[1]]
    assert model.selected_features(assignment) == [model.features[features[0]]]


def test_top_variable_without_auxiliary_variables_is_the_feature_count():
    model = FmToPysat(_fm(_UVL), cnf_method='distributive').transform()
    assert model.top_variable() == len(model.variables)


@pytest.mark.parametrize('method', METHODS)
def test_configurations_count_and_sampling_match_distributive(method):
    fm = _fm(_UVL)
    reference = FmToPysat(fm, cnf_method='distributive').transform()
    model = FmToPysat(fm, cnf_method=method).transform()
    expected = _configs(PySATConfigurations().execute(reference).get_result())
    assert _configs(PySATConfigurations().execute(model).get_result()) == expected
    assert PySATConfigurationsNumber().execute(model).get_result() == len(expected)
    sampling = PySATSampling()
    sampling.set_sample_size(5)
    sample = _configs(sampling.execute(model).get_result())
    assert len(sample) == 5 and sample <= expected


@pytest.mark.parametrize('method', METHODS)
def test_filter_reports_features_only(method):
    fm = _fm(_UVL)
    expected = PySATFilter()
    expected.set_configuration(Configuration({'A': True}))
    expected = expected.execute(FmToPysat(fm).transform()).get_result()
    operation = PySATFilter()
    operation.set_configuration(Configuration({'A': True}))
    products = operation.execute(FmToPysat(fm, cnf_method=method).transform()).get_result()
    names = {feature.name for feature in fm.get_features()}
    assert all(None not in product and set(product) <= names for product in products)
    assert sorted(map(sorted, products)) == sorted(map(sorted, expected))


def test_enumeration_is_projected_on_the_features():
    """A free auxiliary variable must not split one configuration into several."""
    fm = _fm(_UVL)
    expected = PySATConfigurationsNumber().execute(FmToPysat(fm).transform()).get_result()
    model = FmToPysat(fm, cnf_method='tseytin').transform()
    free = model.top_variable() + 1
    model.auxiliary_variables.add(free)
    model.add_clause([model.variables['A'], free])  # `free` is unconstrained when A holds
    assert PySATConfigurationsNumber().execute(model).get_result() == expected
    assert len(PySATConfigurations().execute(model).get_result()) == expected


def _hsdag(operation, model):
    checker, tree = operation.prepare_hsdag(model)
    try:
        tree.construct()
        names = model.constraint_assumption_map
        return (sorted(sorted(names[i] for i in d) for d in tree.get_diagnoses()),
                sorted(sorted(names[i] for i in c) for c in tree.get_conflicts()))
    finally:
        checker.delete()


def test_diagnosis_does_not_confuse_selectors_with_auxiliary_variables():
    # 'tseytin' only: on this model 'auto' keeps every constraint distributive.
    method = 'tseytin'
    fm = _fm(_VOID_UVL)
    for operation in (PySATDiagnosis, PySATConflict):
        expected = _hsdag(operation(), FmToDiagPysat(fm).transform())
        got = _hsdag(operation(), FmToDiagPysat(fm, cnf_method=method).transform())
        assert got == expected
    model = FmToDiagPysat(fm, cnf_method=method).transform()
    model.prepare_diagnosis_task()
    selectors = set(model.get_b()) | set(model.get_c())
    assert selectors.isdisjoint(model.auxiliary_variables | set(model.features))


@pytest.mark.parametrize('method', METHODS)
def test_explanations_keep_the_cnf_method(method):
    fm = _fm(_VOID_UVL)
    model = FmToDiagPysat(fm, cnf_method=method).transform()
    assert _prepared_model(model, None).cnf_method == method
    expected = PySATExplainVoidModel().execute(FmToDiagPysat(fm).transform()).get_result()
    assert PySATExplainVoidModel().execute(model).get_result().descriptions() \
        == expected.descriptions()
