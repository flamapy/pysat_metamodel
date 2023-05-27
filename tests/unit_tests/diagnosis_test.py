import unittest

from flamapy.core.discover import DiscoverMetamodels  # This loads the tool in the python execution environment
from flamapy.metamodels.configuration_metamodel.transformations import ConfigurationBasicReader
from flamapy.metamodels.fm_metamodel.transformations import FeatureIDEReader

from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat

from flamapy.metamodels.pysat_metamodel.operations import Glucose3FastDiag, Glucose3QuickXPlain


# def test_with_DiscoverMetamodels():
#     """
#     Won't work because the configuration is not set
#     We want an optional configuration
#     In fact, Glucose3FastDiag implements ValidConfiguration, so it requires a configuration.
#     """
#     dm = DiscoverMetamodels()
#     result = dm.use_operation_from_file("Glucose3FastDiag", "../resources/smartwatch_inconsistent.fide")
#     print(result)
#     result = dm.use_operation_from_file("Glucose3FastDiag", "../resources/smartwatch_consistent.fide")
#     print(result)
#     assert result == ['Diagnosis: [[-8, -4]]']


def test_fastdiag():
    feature_model = FeatureIDEReader("../resources/smartwatch_inconsistent.fide").transform()
    model = FmToPysat(feature_model).transform()

    fastdiag = Glucose3FastDiag()
    fastdiag.execute(model)
    result = fastdiag.get_result()

    print(result)
    assert result == ['Diagnosis: [(3) OR[NOT[Analog][]][NOT[Cellular][]]]']


def test_fastdiag_with_configuration():
    feature_model = FeatureIDEReader("../resources/smartwatch_consistent.fide").transform()
    model = FmToPysat(feature_model).transform()

    configuration = ConfigurationBasicReader("../resources/smartwatch_nonvalid.csvconf").transform()

    fastdiag = Glucose3FastDiag()
    fastdiag.set_configuration(configuration)
    fastdiag.execute(model)
    result = fastdiag.get_result()

    print(result)
    assert result == ['Diagnosis: [E-ink = true]']


def test_fastdiag_with_test_case():
    feature_model = FeatureIDEReader("../resources/smartwatch_consistent.fide").transform()
    model = FmToPysat(feature_model).transform()

    test_case = ConfigurationBasicReader("../resources/smartwatch_testcase.csvconf").transform()

    fastdiag = Glucose3FastDiag()
    fastdiag.set_test_case(test_case)
    fastdiag.execute(model)
    result = fastdiag.get_result()

    print(result)
    assert result == ['Diagnosis: [(3) OR[NOT[Analog][]][NOT[Cellular][]]]']


def test_quickxplain():
    feature_model = FeatureIDEReader("../resources/smartwatch_inconsistent.fide").transform()
    model = FmToPysat(feature_model).transform()

    quickxplain = Glucose3QuickXPlain()
    quickxplain.execute(model)
    result = quickxplain.get_result()

    print(result)
    assert result == ['Conflicts: [(3) OR[NOT[Analog][]][NOT[Cellular][]],(4) IMPLIES[Smartwatch][Cellular],(5) IMPLIES[Smartwatch][Analog]]']


def test_quickxplain_with_configuration():
    feature_model = FeatureIDEReader("../resources/smartwatch_inconsistent.fide").transform()
    model = FmToPysat(feature_model).transform()

    configuration = ConfigurationBasicReader("../resources/smartwatch_nonvalid.csvconf").transform()

    quickxplain = Glucose3QuickXPlain()
    quickxplain.set_configuration(configuration)
    quickxplain.execute(model)
    result = quickxplain.get_result()

    print(result)
    assert result == ['Conflicts: [E-ink = true]']


def test_quickxplain_with_testcase():
    feature_model = FeatureIDEReader("../resources/smartwatch_inconsistent.fide").transform()
    model = FmToPysat(feature_model).transform()

    test_case = ConfigurationBasicReader("../resources/smartwatch_testcase.csvconf").transform()

    quickxplain = Glucose3QuickXPlain()
    quickxplain.set_test_case(test_case)
    quickxplain.execute(model)
    result = quickxplain.get_result()

    print(result)
    assert result == ['Conflicts: [(3) OR[NOT[Analog][]][NOT[Cellular][]]]']


if __name__ == '__main__':
    unittest.main()
