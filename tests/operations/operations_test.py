from famapy.core.models.configuration import Configuration

from famapy.metamodels.fm_metamodel.models.feature_model import Feature
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_core_features import Glucose3CoreFeatures
from famapy.metamodels.pysat_metamodel.operations.glucose3_dead_features import Glucose3DeadFeatures
from famapy.metamodels.pysat_metamodel.operations.glucose3_error_detection import Glucose3ErrorDetection
from famapy.metamodels.pysat_metamodel.operations.glucose3_error_diagnosis import Glucose3ErrorDiagnosis
from famapy.metamodels.pysat_metamodel.operations.glucose3_false_optional_features import Glucose3FalseOptionalFeatures
from famapy.metamodels.pysat_metamodel.operations.glucose3_filter import Glucose3Filter
from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products
from famapy.metamodels.pysat_metamodel.operations.glucose3_products_number import Glucose3ProductsNumber
from famapy.metamodels.pysat_metamodel.operations.glucose3_valid import Glucose3Valid
from famapy.metamodels.pysat_metamodel.operations.glucose3_valid_product import Glucose3ValidProduct


def run(model: PySATModel, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_product_list, expected_non_valid_product_list) -> None:

    if expected_core_features is not None:
        core_features = Glucose3CoreFeatures()
        core_features.execute(model)
        assert(core_features.get_result() == expected_core_features)

    if expected_dead_features is not None:
        dead_features = Glucose3DeadFeatures()
        dead_features.execute(model)
        assert(dead_features.get_result() == expected_dead_features)

    if expected_error_detection is not None:
        error_detection = Glucose3ErrorDetection()
        error_detection.execute(model)
        assert(error_detection.get_result() == expected_error_detection)

    if expected_error_diagnosis is not None:
        error_diagnosis = Glucose3ErrorDiagnosis()
        error_diagnosis.execute(model)
        assert(error_diagnosis.get_result() == expected_error_diagnosis)

    if expected_false_optional_features is not None:
        false_optional_features = Glucose3FalseOptionalFeatures()
        false_optional_features.execute(model)
        assert(false_optional_features.get_result()
               == expected_false_optional_features)

    if expected_products_number is not None:
        products_number = Glucose3ProductsNumber()
        products_number.execute(model)
        assert(products_number.get_result() == expected_products_number)

    if expected_products is not None:
        products = Glucose3Products()
        products.execute(model)
        assert(products.get_result() == expected_products)

    if expected_valid is not None:
        valid = Glucose3Valid()
        valid.execute(model)
        assert(valid.result == expected_valid)

    if expected_valid_product_list is not None:
        for product in expected_valid_product_list:
            valid_product = Glucose3ValidProduct()
            valid_product.set_configuration(product)
            valid_product.execute(model)
            assert(valid_product.result)

    if expected_non_valid_product_list is not None:
        for product in expected_non_valid_product_list:
            valid_product = Glucose3ValidProduct()
            valid_product.set_configuration(product)
            valid_product.execute(model)
            assert(not valid_product.result)


def test_error_guessing_core_features_case_1() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-3, 2]]

    expected_core_features = ['A', 'B']
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_core_features_case_2() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B'}
    model.variables = {'A': 1, 'B': 2}
    model.r_cnf.clauses = [[1], [-2, 1]]

    model.ctc_cnf.clauses = [[-1, 2]]

    expected_core_features = ['A', 'B']
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_core_features_case_3() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = ['A', 'B', 'C']
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_core_features_case_4() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3],
                           [-3, 1], [-3, 4, 5], [-4, -5], [-4, 3], [-5, 3]]

    model.ctc_cnf.clauses = [[-2, -4]]

    expected_core_features = ['A', 'B', 'C', 'E']
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_core_features_case_5() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3],
                           [-3, 1], [-3, 4, 5], [-4, -5], [-4, 3], [-5, 3]]

    model.ctc_cnf.clauses = [[-2, 4]]

    expected_core_features = ['A', 'B', 'C', 'D']
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_core_features_case_6() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, -3]]

    expected_core_features = []
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_1() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3],
                           [-3, 1], [-3, 4, 5], [-4, -5], [-4, 3], [-5, 3]]

    model.ctc_cnf.clauses = [[-4, -2]]

    expected_core_features = None
    expected_dead_features = ['D']
    expected_error_detection = ["Dead features: ['D']",
                                "False optional features: ['E']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_2() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3],
                           [-3, 1], [-3, 4, 5], [-4, -5], [-4, 3], [-5, 3]]

    model.ctc_cnf.clauses = [[-2, 4]]

    expected_core_features = None
    expected_dead_features = ['E']
    expected_error_detection = ["Dead features: ['E']",
                                "False optional features: ['D']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_3() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3],
                           [-3, 1], [-3, 4, 5], [-4, 3], [-5, 3]]

    model.ctc_cnf.clauses = [[-4, -2]]

    expected_core_features = None
    expected_dead_features = ['D']
    expected_error_detection = ["Dead features: ['D']",
                                "False optional features: ['E']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_4() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, -3]]

    expected_core_features = None
    expected_dead_features = ["C"]
    expected_error_detection = ["Dead features: ['C']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_5() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, -3]]

    expected_core_features = None
    expected_dead_features = ['A', 'B', 'C']
    expected_error_detection = ["The model is void, so have not any product"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_6() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3],
                           [-2, -3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = None
    expected_dead_features = ['B']
    expected_error_detection = ["Dead features: ['B']",
                                "False optional features: ['C']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_7() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-2, 3], [-3, 2]]

    model.ctc_cnf.clauses = [[-2, -3]]

    expected_core_features = None
    expected_dead_features = ['A', 'B', 'C']
    expected_error_detection = ['The model is void, so have not any product']
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_dead_features_8() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, -3], [-2, 3]]

    expected_core_features = None
    expected_dead_features = ['B']
    expected_error_detection = ["Dead features: ['B']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_false_optional_features_1() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = None
    expected_dead_features = None
    # TODO: False optional features are not detected by error detection operation
    expected_error_detection = [
        "False optional features: ['C']"]
    expected_error_diagnosis = None
    # TODO: False optional features are not detected by optional features operation
    expected_false_optional_features = ['C']
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_false_optional_features_2() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-3, 1],
                           [-3, 4, 5], [-4, -5], [-4, 3], [-5, 3]]

    model.ctc_cnf.clauses = [[-2, 4]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = ["Dead features: ['E']",
                                "False optional features: ['C', 'D']"]
    expected_error_diagnosis = None
    expected_false_optional_features = ['C', 'D']
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_false_optional_features_3() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1],
                           [-3, 1], [-3, 4, 5], [-4, 3], [-5, 3]]

    model.ctc_cnf.clauses = [[-2, 4]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = [
        "False optional features: ['C', 'D']"]
    expected_error_diagnosis = None
    expected_false_optional_features = ['C', 'D']
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_false_optional_features_4() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3],
                           [-2, -3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = ["Dead features: ['B']",
                                "False optional features: ['C']"]
    expected_error_diagnosis = None
    expected_false_optional_features = ['C']
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_false_optional_features_5() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = [
        "False optional features: ['C']"]
    expected_error_diagnosis = None
    expected_false_optional_features = ['C']
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_false_optional_features_6() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'E', 5: 'F', 6: 'D'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'E': 4, 'F': 5, 'D': 6}
    model.r_cnf.clauses = [[1], [-2, 1], [-1, 3], [-3, 1], [-3, 4, 5],
                           [-4, -5], [-4, 3], [-5, 3], [-1, 6], [-6, 1]]

    model.ctc_cnf.clauses = [[-4, 2], [-6, -5]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = ["Dead features: ['F']",
                                "False optional features: ['B', 'E']"]
    expected_error_diagnosis = None
    expected_false_optional_features = ['B', 'E']
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_redundancies_case_1() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-2, 1], [-1, 3], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = None
    expected_dead_features = None
    # TODO: Redundancies not detected by error detection operation
    expected_error_detection = ["Redundancies: ['B requires C']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_error_guessing_redundancies_case_2() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
    model.r_cnf.clauses = [[1], [-2, 1], [-1, 3], [-3, 1], [-1, 4], [-4, 1]]

    model.ctc_cnf.clauses = [[-3, 2], [-4, 2]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = ["False optional features: ['B']",
                                "Redundancies: ['D requires B']"]
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_refinement_alternative_no_or() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-2, 3, 4],
                           [-3, -4], [-3, 2], [-4, 2], [-1, 5], [-5, 1]]

    model.ctc_cnf.clauses = [[-5, 3], [-5, 4]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_refinement_alternative_no_parent_last_child() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-2, 1], [-2, 3, 4], [-3, -4],
                           [-3, 2], [-4, 2], [-1, 5], [-5, 1]]

    model.ctc_cnf.clauses = [[-5, -2], [-5, 4]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('D', []): True, Feature('E', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_refinement_alternative_odd_children() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C',
                      4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
    model.variables = {'A': 1, 'B': 2, 'C': 3,
                       'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-2, 3, 4, 5, 6, 7], [-3, -4], [-3, -5], [-3, -6], [-3, -7], [-3, 2], [-4, -5],
                           [-4, -6], [-4, -7], [-4, 2], [-5, -6], [-5, -7], [-5, 2], [-6, -7], [-6, 2], [-7, 2], [-1, 8], [-8, 1]]

    model.ctc_cnf.clauses = [[-8, 7], [-8, 5]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 0
    expected_products = []
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('E', []): True, Feature('G', []): True, Feature('H', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_refinement_df_alternative_excludes() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-3, 1],
                           [-3, 4, 5], [-4, -5], [-4, 3], [-5, 3], [-2, 4]]

    model.ctc_cnf.clauses = [[-2, 4]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_refinement_optional_alternative_valid_p() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
    model.r_cnf.clauses = [[1], [-2, 1],
                           [-2, 3, 4], [-3, -4], [-3, 2], [-4, 2]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('C', []): True, Feature('D', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_refinement_or_no_alternative() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1],
                           [-2, 3, 4], [-3, 2], [-4, 2], [-1, 5], [-5, 1]]

    model.ctc_cnf.clauses = [[-5, 3], [-5, 4]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_allrelationships() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'D', 4: 'E', 5: 'C', 6: 'F', 7: 'G'}
    model.variables = {'A': 1, 'B': 2, 'D': 3, 'E': 4, 'C': 5, 'F': 6, 'G': 7}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-2, 3, 4], [-3, -4], [-3,
                                                                         2], [-4, 2], [-5, 1], [-5, 6, 7], [-6, 5], [-7, 5]]

    model.ctc_cnf.clauses = [[-4, 6], [-3, -7]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 4
    expected_products = [['A', 'B', 'D'], ['A', 'B', 'D', 'C', 'F'], [
        'A', 'B', 'E', 'C', 'F'], ['A', 'B', 'E', 'C', 'F', 'G']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('D', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('E', []): True, Feature('F', []): True, Feature('G', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('D', []): True, Feature('E', []): True, Feature('F', []): True, Feature('G', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_alternative() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, -3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [['A', 'B'], ['A', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True}), Configuration({Feature('A', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_alternative_excludes() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3],
                           [-2, -3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, -3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [['A', 'B'], ['A', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_alternative_requires() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'C', 3: 'B'}
    model.variables = {'A': 1, 'C': 2, 'B': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, -3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-3, 2]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 1
    expected_products = [['A', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('C', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_excludes() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, -3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 3
    expected_products = [['A'], ['A', 'C'], ['A', 'B']]
    expected_valid = True
    expected_valid_products = [Configuration({Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('C', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_mandatory() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B'}
    model.variables = {'A': 1, 'B': 2}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 1
    expected_products = [['A', 'B']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_mandatory_alternative() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'E', 4: 'F', 5: 'C', 6: 'D', 7: 'G'}
    model.variables = {'A': 1, 'B': 2, 'E': 3, 'F': 4, 'C': 5, 'D': 6, 'G': 7}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-2, 3, 4], [-3, -4], [-3,
                                                                         2], [-4, 2], [-1, 5, 6], [-5, -6], [-5, 1], [-6, 1], [-5, 7], [-7, 5]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 4
    expected_products = [['A', 'B', 'E', 'D'], ['A', 'B', 'E', 'C', 'G'], [
        'A', 'B', 'F', 'C', 'G'], ['A', 'B', 'F', 'D']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('D', []): True, Feature('E', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('E', []): True, Feature('G', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('F', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('D', []): True, Feature('E', []): True, Feature('G', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_mandatory_excludes() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3], [-3, 1], [-2, -3]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 0
    expected_products = []
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_mandatory_optional() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'D', 4: 'C', 5: 'E'}
    model.variables = {'A': 1, 'B': 2, 'D': 3, 'C': 4, 'E': 5}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1],
                           [-3, 2], [-4, 1], [-4, 5], [-5, 4]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 4
    expected_products = [['A', 'B'], [
        'A', 'B', 'C', 'E'], ['A', 'B', 'D', 'C', 'E'],  ['A', 'B', 'D']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('D', []): True, Feature('E', []): True})]
    expected_non_valid_products = [Configuration({Feature('A', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_mandatory_or() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'E', 4: 'F', 5: 'C', 6: 'D', 7: 'G'}
    model.variables = {'A': 1, 'B': 2, 'E': 3, 'F': 4, 'C': 5, 'D': 6, 'G': 7}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-2, 3, 4], [-3,
                                                               2], [-4, 2], [-1, 5, 6], [-5, 1], [-6, 1], [-6, 7], [-7, 6]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 9
    expected_products = [['A', 'B', 'E', 'C'], ['A', 'B', 'E', 'F', 'C'], ['A', 'B', 'E', 'F', 'C', 'D', 'G'], ['A', 'B', 'F', 'C'], [
        'A', 'B', 'E', 'C', 'D', 'G'], ['A', 'B', 'E', 'D', 'G'], ['A', 'B', 'E', 'F', 'D', 'G'], ['A', 'B', 'F', 'C', 'D', 'G'], ['A', 'B', 'F', 'D', 'G']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('F', []): True}),
        Configuration({Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('D', []): True, Feature('E', []): True, Feature('F', []): True, Feature('G', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_mandatory_requires() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2], [-2, 1], [-1, 3], [-3, 1], [-2, 3]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 1
    expected_products = [['A', 'B', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]
    expected_non_valid_products = [Configuration({Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_optional() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B'}
    model.variables = {'A': 1, 'B': 2}
    model.r_cnf.clauses = [[1], [-2, 1]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [['A'], ['A', 'B']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True}), Configuration(
        {Feature('A', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('B', []): True}), Configuration(
        {Feature('A', []): True, Feature('H', []): True})]  # TODO: Fix products with non-existent features being calculated as valid

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_optional_alternative() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'E', 4: 'F', 5: 'C', 6: 'D', 7: 'G'}
    model.variables = {'A': 1, 'B': 2, 'E': 3, 'F': 4, 'C': 5, 'D': 6, 'G': 7}
    model.r_cnf.clauses = [[1], [-2, 1], [-2, 3, 4], [-3, -4], [-3,
                                                                2], [-4, 2], [-1, 5, 6], [-5, -6], [-5, 1], [-6, 1], [-7, 6]]
    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 9
    expected_products = [['A', 'C'], ['A', 'D'], ['A', 'B', 'E', 'C'], ['A', 'B', 'E', 'D'], [
        'A', 'B', 'E', 'D', 'G'], ['A', 'B', 'F', 'D', 'G'], ['A', 'B', 'F', 'D'], ['A', 'D', 'G'], ['A', 'B', 'F', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('C', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('D', []): True, Feature('F', []): True, Feature('G', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('D', []): True, Feature('E', []): True, Feature('F', []): True, Feature('G', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_optional_or() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'E', 4: 'F', 5: 'C', 6: 'D', 7: 'G'}
    model.variables = {'A': 1, 'B': 2, 'E': 3, 'F': 4, 'C': 5, 'D': 6, 'G': 7}
    model.r_cnf.clauses = [[1], [-2, 1], [-2, 3, 4], [-3,
                                                      2], [-4, 2], [-1, 5, 6], [-5, 1], [-6, 1], [-7, 5]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 20
    expected_products = [['A', 'C'], ['A', 'C', 'D'], ['A', 'C', 'D', 'G'], ['A', 'C', 'G'], ['A', 'B', 'F', 'C', 'G'], ['A', 'B', 'E', 'F', 'C', 'G'], ['A', 'B', 'E', 'F', 'C'], ['A', 'B', 'E', 'F', 'C', 'D'], ['A', 'B', 'E', 'C', 'D'], ['A', 'B', 'F', 'C', 'D'], [
        'A', 'B', 'F', 'C', 'D', 'G'], ['A', 'B', 'F', 'D'], ['A', 'B', 'F', 'C'], ['A', 'B', 'E', 'C'], ['A', 'B', 'E', 'C', 'G'], ['A', 'B', 'E', 'C', 'D', 'G'], ['A', 'B', 'E', 'D'], ['A', 'B', 'E', 'F', 'D'], ['A', 'B', 'E', 'F', 'C', 'D', 'G'], ['A', 'D']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('C', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True, Feature('D', []): True, Feature('E', []): True, Feature('F', []): True, Feature('G', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_or() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 3
    expected_products = [['A', 'B'], ['A', 'B', 'C'], ['A', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]
    expected_non_valid_products = [Configuration({Feature('A', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_or_alternative() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C', 4: 'F',
                      5: 'G', 6: 'D', 7: 'E', 8: 'H', 9: 'I'}
    model.variables = {'A': 1, 'B': 2, 'C': 3, 'F': 4,
                       'G': 5, 'D': 6, 'E': 7, 'H': 8, 'I': 9}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, -3], [-2, 1], [-3, 1], [-2, 4, 5], [-4,
                                                                                     2], [-5, 2], [-1, 6, 7], [-6, 1], [-7, 1], [-7, 8, 9], [-8, -9], [-8, 7], [-9, 7]]

    model.ctc_cnf.clauses = []

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 20
    expected_products = [['A', 'C', 'D'], ['A', 'C', 'D', 'E', 'H'], ['A', 'C', 'D', 'E', 'I'], ['A', 'B', 'F', 'D', 'E', 'I'], ['A', 'B', 'F', 'G', 'D', 'E', 'I'], ['A', 'B', 'F', 'G', 'D'], ['A', 'B', 'G', 'D'], ['A', 'B', 'G', 'D', 'E', 'I'], ['A', 'B', 'F', 'D'], ['A', 'B', 'F', 'E', 'I'], [
        'A', 'B', 'F', 'E', 'H'], ['A', 'B', 'F', 'D', 'E', 'H'], ['A', 'C', 'E', 'H'], ['A', 'C', 'E', 'I'], ['A', 'B', 'G', 'E', 'I'], ['A', 'B', 'F', 'G', 'E', 'I'], ['A', 'B', 'F', 'G', 'D', 'E', 'H'], ['A', 'B', 'F', 'G', 'E', 'H'], ['A', 'B', 'G', 'E', 'H'], ['A', 'B', 'G', 'D', 'E', 'H']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('C', []): True, Feature('D', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('D', []): True, Feature('E', []): True, Feature('F', []): True, Feature('G', []): True, Feature('H', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('C', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('D', []): True, Feature('E', []): True, Feature('F', []): True, Feature('G', []): True, Feature('H', []): True, Feature('I', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_or_excludes() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, -3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_or_requires() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [['A', 'B', 'C'], ['A', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True, Feature('C', []): True}, ), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]
    expected_non_valid_products = [Configuration({Feature('A', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_requires() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 3
    expected_products = [['A'], ['A', 'C'], ['A', 'B', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]
    expected_non_valid_products = None

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)


def test_relationships_requires_excludes() -> None:

    model = PySATModel()

    model.features = {1: 'A', 2: 'B', 3: 'C'}
    model.variables = {'A': 1, 'B': 2, 'C': 3}
    model.r_cnf.clauses = [[1], [-2, 1], [-3, 1]]

    model.ctc_cnf.clauses = [[-2, 3], [-2, -3]]

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [['A'], ['A', 'C']]
    expected_valid = True
    expected_valid_products = [Configuration(
        {Feature('A', []): True}), Configuration(
        {Feature('A', []): True, Feature('C', []): True})]
    expected_non_valid_products = [Configuration(
        {Feature('A', []): True, Feature('B', []): True, Feature('C', []): True})]

    run(model, expected_core_features, expected_dead_features, expected_error_detection, expected_error_diagnosis, expected_false_optional_features,
        expected_products_number, expected_products, expected_valid, expected_valid_products, expected_non_valid_products)
