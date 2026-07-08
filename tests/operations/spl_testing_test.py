from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.fm_metamodel.transformations import FeatureIDEReader
from flamapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import (
    PySATCoverage,
    PySATCoveringArray,
    PySATSampleReduction,
)


def _sat_model(path="./tests/resources/pizzas.fide"):
    return FmToPysat(FeatureIDEReader(path).transform()).transform()


def _covering_array(model, t=2, seed=None):
    operation = PySATCoveringArray()
    operation.set_t(t)
    if seed is not None:
        operation.set_seed(seed)
    return operation.execute(model).get_result()


def _coverage(model, configurations, t=2):
    operation = PySATCoverage()
    operation.set_t(t)
    operation.set_configurations(configurations)
    return operation.execute(model).get_result()


def _reduce(model, configurations, t=2):
    operation = PySATSampleReduction()
    operation.set_t(t)
    operation.set_configurations(configurations)
    return operation.execute(model).get_result()


def test_covering_array_achieves_full_coverage():
    # The built-in cross-check: a t=2 covering array must measure 100% coverage.
    model = _sat_model()
    array = _covering_array(model, t=2)
    assert array
    assert _coverage(model, array, t=2) == 1.0


def test_covering_array_is_reproducible_per_seed():
    model = _sat_model()
    first = _covering_array(model, t=2, seed=42)
    second = _covering_array(model, t=2, seed=42)
    assert [c.elements for c in first] == [c.elements for c in second]
    # A different seed still yields a (possibly different) full covering array.
    other = _covering_array(model, t=2, seed=7)
    assert _coverage(model, other, t=2) == 1.0


def test_partial_suite_measures_partial_coverage():
    model = _sat_model()
    array = _covering_array(model, t=2)
    partial = array[:1]
    coverage = _coverage(model, partial, t=2)
    assert 0.0 < coverage < 1.0


def test_reduction_preserves_coverage_with_fewer_configurations():
    model = _sat_model()
    array = _covering_array(model, t=2)
    # A redundant suite: the array twice over.
    redundant = array + array
    reduced = _reduce(model, redundant, t=2)
    assert len(reduced) < len(redundant)
    assert _coverage(model, reduced, t=2) == _coverage(model, redundant, t=2) == 1.0


def test_reduction_preserves_partial_coverage():
    model = _sat_model()
    array = _covering_array(model, t=2)
    partial = array[:2] + array[:2]  # duplicated partial suite
    reduced = _reduce(model, partial, t=2)
    assert len(reduced) <= 2
    assert _coverage(model, reduced, t=2) == _coverage(model, partial, t=2)


def test_coverage_accepts_dict_configurations():
    model = _sat_model()
    array = _covering_array(model, t=1)
    as_dicts = [Configuration(dict(c.elements)) for c in array]
    assert _coverage(model, as_dicts, t=1) == 1.0
