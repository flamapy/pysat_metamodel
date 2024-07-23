import unittest

from flamapy.metamodels.configuration_metamodel.transformations import ConfigurationBasicReader
from flamapy.metamodels.fm_metamodel.transformations import FeatureIDEReader
from flamapy.metamodels.pysat_diagnosis_metamodel.transformations import FmToDiagPysat

from flamapy.metamodels.pysat_diagnosis_metamodel.operations import PySATDiagnosis, PySATConflict


def test_fastdiag_all():
    """
    Identify all diagnoses
    """
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_inconsistent.fide").transform()
    print("numer of feats " + str(len(feature_model.get_features())))
    print(feature_model)
    model = FmToDiagPysat(feature_model).transform()

    hsdag_fastdiag = PySATDiagnosis()
    hsdag_fastdiag.execute(model)
    result = hsdag_fastdiag.get_result()

    print(result)
    assert result == ['Diagnoses: [(5) IMPLIES[Smartwatch][Analog]],[(4) IMPLIES[Smartwatch][Cellular]],[(3) OR[NOT[Analog][]][NOT[Cellular][]]]',
                      'Conflict: [(5) IMPLIES[Smartwatch][Analog], (4) IMPLIES[Smartwatch][Cellular], (3) OR[NOT[Analog][]][NOT[Cellular][]]]']


def test_fastdiag_one():
    """
    Identify one diagnosis
    """
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_inconsistent.fide").transform()
    model = FmToDiagPysat(feature_model).transform()

    hsdag_fastdiag = PySATDiagnosis()
    hsdag_fastdiag.max_diagnoses = 1
    hsdag_fastdiag.execute(model)
    result = hsdag_fastdiag.get_result()

    print(result)
    assert result == ['Diagnosis: [(5) IMPLIES[Smartwatch][Analog]]',
                      'No conflicts found']


def test_fastdiag_two():
    """
    Identify two diagnoses
    """
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_inconsistent.fide").transform()
    model = FmToDiagPysat(feature_model).transform()

    hsdag_fastdiag = PySATDiagnosis()
    hsdag_fastdiag.max_diagnoses = 2
    hsdag_fastdiag.execute(model)
    result = hsdag_fastdiag.get_result()

    print(result)
    assert result == ['Diagnoses: [(5) IMPLIES[Smartwatch][Analog]],[(4) IMPLIES[Smartwatch][Cellular]]',
                      'No conflicts found']


def test_quickxplain_all():
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_inconsistent.fide").transform()

    model = FmToDiagPysat(feature_model).transform()

    hsdag_quickxplain = PySATConflict()
    hsdag_quickxplain.execute(model)
    result = hsdag_quickxplain.get_result()

    print(result)
    assert result == [
        'Conflict: [(5) IMPLIES[Smartwatch][Analog], (4) IMPLIES[Smartwatch][Cellular], (3) OR[NOT[Analog][]][NOT[Cellular][]]]',
        'Diagnoses: [(5) IMPLIES[Smartwatch][Analog]],[(4) IMPLIES[Smartwatch][Cellular]],[(3) OR[NOT[Analog][]][NOT[Cellular][]]]']


def test_quickxplain_one():
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_inconsistent.fide").transform()
    model = FmToDiagPysat(feature_model).transform()

    hsdag_quickxplain = PySATConflict()
    hsdag_quickxplain.max_conflicts = 1
    hsdag_quickxplain.execute(model)
    result = hsdag_quickxplain.get_result()

    print(result)
    assert result == [
        'Conflict: [(5) IMPLIES[Smartwatch][Analog], (4) IMPLIES[Smartwatch][Cellular], (3) OR[NOT[Analog][]][NOT[Cellular][]]]',
        'No diagnosis found']


def test_quickxplain_two():
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_inconsistent.fide").transform()
    model = FmToDiagPysat(feature_model).transform()

    hsdag_quickxplain = PySATConflict()
    hsdag_quickxplain.max_conflicts = 2
    hsdag_quickxplain.execute(model)
    result = hsdag_quickxplain.get_result()

    print(result)
    assert result == [
        'Conflict: [(5) IMPLIES[Smartwatch][Analog], (4) IMPLIES[Smartwatch][Cellular], (3) OR[NOT[Analog][]][NOT[Cellular][]]]',
        'Diagnoses: [(5) IMPLIES[Smartwatch][Analog]],[(4) IMPLIES[Smartwatch][Cellular]],[(3) OR[NOT[Analog][]][NOT[Cellular][]]]']


def test_fastdiag_with_configuration():
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_consistent.fide").transform()
    model = FmToDiagPysat(feature_model).transform()
    configuration = ConfigurationBasicReader("./tests/resources/smartwatch_nonvalid.csvconf").transform()
    
    hsdag_fastdiag = PySATDiagnosis()
    hsdag_fastdiag.set_configuration(configuration)

    hsdag_fastdiag.execute(model)
    result = hsdag_fastdiag.get_result()

    assert result == ['Diagnoses: [E-ink = true],[Analog = true]',
                      'Conflict: [E-ink = true, Analog = true]']


def test_quickxplain_with_configuration():
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_consistent.fide").transform()
    model = FmToDiagPysat(feature_model).transform()

    configuration = ConfigurationBasicReader("./tests/resources/smartwatch_nonvalid.csvconf").transform()

    hsdag_quickxplain = PySATConflict()
    hsdag_quickxplain.set_configuration(configuration)
    hsdag_quickxplain.execute(model)
    result = hsdag_quickxplain.get_result()

    print(result)
    assert result == ['Conflict: [E-ink = true, Analog = true]', 'Diagnoses: [E-ink = true],[Analog = true]']


def test_fastdiag_with_test_case():
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_deadfeature.fide").transform()
    model = FmToDiagPysat(feature_model).transform()

    test_case = ConfigurationBasicReader("./tests/resources/smartwatch_testcase.csvconf").transform()

    hsdag_fastdiag = PySATDiagnosis()
    hsdag_fastdiag.set_test_case(test_case)
    hsdag_fastdiag.execute(model)
    result = hsdag_fastdiag.get_result()

    print(result)
    assert result == ['Diagnoses: [(4) IMPLIES[Smartwatch][Analog]],'
                      '[(alternative) Screen[1,1]Analog High Resolution E-ink ]',
                      'Conflict: [(4) IMPLIES[Smartwatch][Analog], '
                      '(alternative) Screen[1,1]Analog High Resolution E-ink ]']


def test_quickxplain_with_testcase():
    feature_model = FeatureIDEReader("./tests/resources/smartwatch_deadfeature.fide").transform()
    model = FmToDiagPysat(feature_model).transform()

    test_case = ConfigurationBasicReader("./tests/resources/smartwatch_testcase.csvconf").transform()

    hsdag_quickxplain = PySATConflict()
    hsdag_quickxplain.set_test_case(test_case)
    hsdag_quickxplain.execute(model)
    result = hsdag_quickxplain.get_result()

    print(result)
    assert result == ['Conflict: [(4) IMPLIES[Smartwatch][Analog], '
                      '(alternative) Screen[1,1]Analog High Resolution E-ink ]',
                      'Diagnoses: [(4) IMPLIES[Smartwatch][Analog]],'
                      '[(alternative) Screen[1,1]Analog High Resolution E-ink ]']


if __name__ == '__main__':
    unittest.main()
