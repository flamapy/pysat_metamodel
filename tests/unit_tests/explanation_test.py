import pytest

from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.fm_metamodel.transformations import FeatureIDEReader
from flamapy.metamodels.pysat_diagnosis_metamodel.models import Explanation
from flamapy.metamodels.pysat_diagnosis_metamodel.operations import (
    PySATExplainDeadFeature,
    PySATExplainVoidModel,
)
from flamapy.metamodels.pysat_diagnosis_metamodel.transformations import FmToDiagPysat


def _diag_model(path):
    return FmToDiagPysat(FeatureIDEReader(path).transform()).transform()


def test_explain_void_model_on_inconsistent_model():
    model = _diag_model("./tests/resources/smartwatch_inconsistent.fide")
    operation = PySATExplainVoidModel().execute(model)
    explanation = operation.get_result()
    assert isinstance(explanation, Explanation) and explanation
    # The known minimal conflict of this model (same constraints the HSDAG tests report).
    assert set(explanation.descriptions()) == {
        '(5) IMPLIES[Smartwatch][Analog]',
        '(4) IMPLIES[Smartwatch][Cellular]',
        '(3) OR[NOT[Analog][]][NOT[Cellular][]]',
    }
    assert all(item.kind == 'constraint' for item in explanation.items)


def test_explain_void_model_on_consistent_model_is_empty():
    model = _diag_model("./tests/resources/smartwatch_consistent.fide")
    explanation = PySATExplainVoidModel().execute(model).get_result()
    assert not explanation
    assert explanation.descriptions() == []


def test_explain_dead_feature():
    model = _diag_model("./tests/resources/smartwatch_deadfeature.fide")
    operation = PySATExplainDeadFeature()
    operation.set_feature('E-ink')
    explanation = operation.execute(model).get_result()
    assert set(explanation.descriptions()) == {
        '(4) IMPLIES[Smartwatch][Analog]',
        '(alternative) Screen[1,1]Analog High Resolution E-ink',
    }
    kinds = {item.constraint_repr: item.kind for item in explanation.items}
    assert kinds['(4) IMPLIES[Smartwatch][Analog]'] == 'constraint'
    assert kinds['(alternative) Screen[1,1]Analog High Resolution E-ink'] == 'relationship'


def test_explain_not_dead_feature_is_empty():
    model = _diag_model("./tests/resources/smartwatch_deadfeature.fide")
    operation = PySATExplainDeadFeature()
    operation.set_feature('Analog')
    assert not operation.execute(model).get_result()


def test_explain_unknown_feature_raises():
    model = _diag_model("./tests/resources/smartwatch_deadfeature.fide")
    operation = PySATExplainDeadFeature()
    operation.set_feature('NoSuchFeature')
    with pytest.raises(FlamaException):
        operation.execute(model)


def test_repeated_explanations_on_the_same_model_do_not_interfere():
    # prepare_diagnosis_task mutates the model in place; the operations must rebuild a
    # pristine encoding per execution so a (cached) model can serve many calls.
    model = _diag_model("./tests/resources/smartwatch_deadfeature.fide")
    first = PySATExplainDeadFeature()
    first.set_feature('E-ink')
    baseline = set(first.execute(model).get_result().descriptions())

    other = PySATExplainDeadFeature()
    other.set_feature('Analog')
    other.execute(model)

    again = PySATExplainDeadFeature()
    again.set_feature('E-ink')
    assert set(again.execute(model).get_result().descriptions()) == baseline


def test_explanation_str_renders_numbered_lines():
    model = _diag_model("./tests/resources/smartwatch_inconsistent.fide")
    explanation = PySATExplainVoidModel().execute(model).get_result()
    rendered = str(explanation)
    assert rendered.splitlines()[0].startswith('1. ')
    assert len(rendered.splitlines()) == len(explanation.items)
    assert str(Explanation()) == 'No conflict found.'
