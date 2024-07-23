
from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.fm_metamodel.models import Feature
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.pysat_core_features import (
    PySATCoreFeatures,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_dead_features import (
    PySATDeadFeatures,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_false_optional_features import (
    PySATFalseOptionalFeatures,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_configurations import (
    PySATConfigurations,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_configurations_number import (
    PySATConfigurationsNumber,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_satisfiable import PySATSatisfiable
from flamapy.metamodels.pysat_metamodel.operations.pysat_satisfiable_configuration import (
    PySATSatisfiableConfiguration,
)


def run(
    model: PySATModel,
    expected_core_features,
    expected_dead_features,
    expected_error_detection,
    expected_error_diagnosis,
    expected_false_optional_features,
    expected_products_number,
    expected_products,
    expected_valid,
    expected_valid_product_list,
    expected_non_valid_product_list,
) -> None:

    if expected_core_features is not None:
        core_features = PySATCoreFeatures()
        core_features.execute(model)
        assert str(core_features.get_result()) == str(expected_core_features)

    if expected_dead_features is not None:
        dead_features = PySATDeadFeatures()
        dead_features.execute(model)
        assert str(dead_features.get_result()) == str(expected_dead_features)

    if expected_false_optional_features is not None:
        false_optional_features = PySATFalseOptionalFeatures()
        false_optional_features.execute(model)
        assert str(false_optional_features.get_result()) == str(expected_false_optional_features)

    if expected_products_number is not None:
        products_number = PySATConfigurationsNumber()
        products_number.execute(model)
        assert str(products_number.get_result()) == str(expected_products_number)

    if expected_products is not None:
        products = PySATConfigurations()
        products.execute(model)
        assert str(products.get_result()) == str(expected_products)

    if expected_valid is not None:
        valid = PySATSatisfiable()
        valid.execute(model)
        assert valid.result == expected_valid

    if expected_valid_product_list is not None:
        for product in expected_valid_product_list:
            valid_product = PySATSatisfiableConfiguration()
            valid_product.set_configuration(configuration = product, is_full = True)
            valid_product.execute(model)
            assert valid_product.is_satisfiable()

    if expected_non_valid_product_list is not None:
        for product in expected_non_valid_product_list:
            valid_product = PySATSatisfiableConfiguration()
            valid_product.set_configuration(configuration = product, is_full = True)
            valid_product.execute(model)
            assert not valid_product.is_satisfiable()


def test_error_guessing_core_features_case_1() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-3, 2]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = ["A", "B"]
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_error_guessing_core_features_case_2() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B"}
    model.variables = {"A": 1, "B": 2}
    r_cnf_clauses = [[1], [-2, 1]]
    ctc_cnf_clauses = [[-1, 2]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = ["A", "B"]
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_error_guessing_core_features_case_3() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-2, 3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = ["A", "B", "C"]
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_error_guessing_core_features_case_4() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-1, 3],
        [-3, 1],
        [-3, 4, 5],
        [-4, -5],
        [-4, 3],
        [-5, 3],
    ]
    ctc_cnf_clauses = [[-2, -4]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = ["A", "B", "C", "E"]
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_error_guessing_core_features_case_5() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-1, 3],
        [-3, 1],
        [-3, 4, 5],
        [-4, -5],
        [-4, 3],
        [-5, 3],
    ]
    ctc_cnf_clauses = [[-2, 4]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = ["A", "B", "C", "D"]
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = None

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_error_guessing_core_features_case_6() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2], [-2, 1], [-1, 3], [-3, 1]]
    ctc_cnf_clauses = [[-2, -3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

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

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_refinement_alternative_no_or() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-2, 3, 4],
        [-3, -4],
        [-3, 2],
        [-4, 2],
        [-1, 5],
        [-5, 1],
    ]
    ctc_cnf_clauses = [[-5, 3], [-5, 4]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

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

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_refinement_alternative_no_parent_last_child() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    r_cnf_clauses = [
        [1],
        [-2, 1],
        [-2, 3, 4],
        [-3, -4],
        [-3, 2],
        [-4, 2],
        [-1, 5],
        [-5, 1],
    ]
    ctc_cnf_clauses = [[-5, -2], [-5, 4]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = [
        Configuration(
            {"A": True, "D": True, "E": True}
        )
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_refinement_alternative_odd_children() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G", 8: "H"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-2, 3, 4, 5, 6, 7],
        [-3, -4],
        [-3, -5],
        [-3, -6],
        [-3, -7],
        [-3, 2],
        [-4, -5],
        [-4, -6],
        [-4, -7],
        [-4, 2],
        [-5, -6],
        [-5, -7],
        [-5, 2],
        [-6, -7],
        [-6, 2],
        [-7, 2],
        [-1, 8],
        [-8, 1],
    ]
    ctc_cnf_clauses = [[-8, 7], [-8, 5]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 0
    expected_products = []
    expected_valid = False
    expected_valid_products = None
    expected_non_valid_products = [
        Configuration(
            {
                "A": True,
                "B": True,
                "E": True,
                "G": True,
                "H": True,
            }
        )
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_refinement_df_alternative_excludes() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-3, 1],
        [-3, 4, 5],
        [-4, -5],
        [-4, 3],
        [-5, 3],
        [-2, 4],
    ]
    ctc_cnf_clauses = [[-2, 4]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

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

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_refinement_optional_alternative_valid_p() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4}
    r_cnf_clauses = [[1], [-2, 1], [-2, 3, 4], [-3, -4], [-3, 2], [-4, 2]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = None
    expected_non_valid_products = [
        Configuration(
            {"A": True, "C": True, "D": True}
        )
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_refinement_or_no_alternative() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    model.variables = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-2, 3, 4],
        [-3, 2],
        [-4, 2],
        [-1, 5],
        [-5, 1],
    ]
    ctc_cnf_clauses = [[-5, 3], [-5, 4]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

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

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_allrelationships() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "D", 4: "E", 5: "C", 6: "F", 7: "G"}
    model.variables = {"A": 1, "B": 2, "D": 3, "E": 4, "C": 5, "F": 6, "G": 7}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-2, 3, 4],
        [-3, -4],
        [-3, 2],
        [-4, 2],
        [-5, 1],
        [-5, 6, 7],
        [-6, 5],
        [-7, 5],
    ]
    ctc_cnf_clauses = [[-4, 6], [-3, -7]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 4
    expected_products = [
        Configuration({"A":True, "B":True, "D":True}),
        Configuration({"A":True, "B":True, "D":True, "C":True, "F":True}),
        Configuration({"A":True, "B":True, "E":True, "C":True, "F":True}),
        Configuration({"A":True,"B":True, "E":True, "C":True, "F":True, "G":True}),
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration(
            {"A": True, "B": True, "D": True}
        ),
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "E": True,
                "F": True,
                "G": True,
            }
        ),
    ]
    expected_non_valid_products = [
        Configuration({"A": True, "B": True}),
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "D": True,
                "E": True,
                "F": True,
                "G": True,
            }
        ),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_alternative() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2, 3], [-2, -3], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [
        Configuration({"A": True, "B": True}), 
        Configuration({"A": True, "C": True}), 
        ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "B": True})
    ]
    expected_non_valid_products = [
        Configuration(
            {"A": True, "B": True, "C": True}
        ),
        Configuration({"A": True}),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_alternative_excludes() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2, 3], [-2, -3], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-2, -3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [["A", "B"], ["A", "C"]]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "B": True})
    ]
    expected_non_valid_products = [
        Configuration({"A": True}),
        Configuration(
            {"A": True, "B": True, "C": True}
        ),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_alternative_requires() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "C", 3: "B"}
    model.variables = {"A": 1, "C": 2, "B": 3}
    r_cnf_clauses = [[1], [-1, 2, 3], [-2, -3], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-3, 2]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 1
    expected_products = [["A", "C"]]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "C": True})
    ]
    expected_non_valid_products = [
        Configuration({"A": True}),
        Configuration(
            {"A": True, "B": True, "C": True}
        ),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_excludes() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-2, -3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 3
    expected_products = [["A"], ["A", "C"], ["A", "B"]]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True}),
        Configuration({"A": True, "C": True}),
    ]
    expected_non_valid_products = [
        Configuration(
            {"A": True, "B": True, "C": True}
        )
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_mandatory() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B"}
    model.variables = {"A": 1, "B": 2}
    r_cnf_clauses = [[1], [-1, 2], [-2, 1]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 1
    expected_products = [["A", "B"]]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "B": True})
    ]
    expected_non_valid_products = [Configuration({"A": True})]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_mandatory_alternative() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "E", 4: "F", 5: "C", 6: "D", 7: "G"}
    model.variables = {"A": 1, "B": 2, "E": 3, "F": 4, "C": 5, "D": 6, "G": 7}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-2, 3, 4],
        [-3, -4],
        [-3, 2],
        [-4, 2],
        [-1, 5, 6],
        [-5, -6],
        [-5, 1],
        [-6, 1],
        [-5, 7],
        [-7, 5],
    ]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 4
    expected_products = [
        ["A", "B", "E", "D"],
        ["A", "B", "E", "C", "G"],
        ["A", "B", "F", "C", "G"],
        ["A", "B", "F", "D"],
    ]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration(
            {
                "A": True,
                "B": True,
                "D": True,
                "E": True,
            }
        ),
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "E": True,
                "G": True,
            }
        ),
    ]
    expected_non_valid_products = [
        Configuration(
            {"A": True, "B": True, "F": True}
        ),
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "D": True,
                "E": True,
                "G": True,
            }
        ),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_mandatory_excludes() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2], [-2, 1], [-1, 3], [-3, 1], [-2, -3]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

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

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_mandatory_optional() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "D", 4: "C", 5: "E"}
    model.variables = {"A": 1, "B": 2, "D": 3, "C": 4, "E": 5}
    r_cnf_clauses = [[1], [-1, 2], [-2, 1], [-3, 2], [-4, 1], [-4, 5], [-5, 4]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 4
    expected_products = [
        ["A", "B"],
        ["A", "B", "C", "E"],
        ["A", "B", "D", "C", "E"],
        ["A", "B", "D"],
    ]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "B": True}),
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "D": True,
                "E": True,
            }
        ),
    ]
    expected_non_valid_products = [Configuration({"A": True})]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_mandatory_or() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "E", 4: "F", 5: "C", 6: "D", 7: "G"}
    model.variables = {"A": 1, "B": 2, "E": 3, "F": 4, "C": 5, "D": 6, "G": 7}
    r_cnf_clauses = [
        [1],
        [-1, 2],
        [-2, 1],
        [-2, 3, 4],
        [-3, 2],
        [-4, 2],
        [-1, 5, 6],
        [-5, 1],
        [-6, 1],
        [-6, 7],
        [-7, 6],
    ]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 9
    expected_products = [
        ["A", "B", "E", "C"],
        ["A", "B", "E", "F", "C"],
        ["A", "B", "E", "F", "C", "D", "G"],
        ["A", "B", "F", "C"],
        ["A", "B", "E", "C", "D", "G"],
        ["A", "B", "E", "D", "G"],
        ["A", "B", "E", "F", "D", "G"],
        ["A", "B", "F", "C", "D", "G"],
        ["A", "B", "F", "D", "G"],
    ]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "F": True,
            }
        ),
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "D": True,
                "E": True,
                "F": True,
                "G": True,
            }
        ),
    ]
    expected_non_valid_products = [
        Configuration(
            {"A": True, "B": True, "C": True}
        )
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_mandatory_requires() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2], [-2, 1], [-1, 3], [-3, 1], [-2, 3]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 1
    expected_products = [["A", "B", "C"]]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration(
            {"A": True, "B": True, "C": True}
        )
    ]
    expected_non_valid_products = [
        Configuration({"A": True}),
        Configuration({"A": True, "B": True}),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_optional() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B"}
    model.variables = {"A": 1, "B": 2}
    r_cnf_clauses = [[1], [-2, 1]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [["A"], ["A", "B"]]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "B": True}),
        Configuration({"A": True}),
    ]
    expected_non_valid_products = [
        Configuration({"B": True}),
        Configuration({"A": True, "H": True}),
    ]  # TODO: Fix products with non-existent features being calculated as valid

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_optional_alternative() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "E", 4: "F", 5: "C", 6: "D", 7: "G"}
    model.variables = {"A": 1, "B": 2, "E": 3, "F": 4, "C": 5, "D": 6, "G": 7}
    r_cnf_clauses = [
        [1],
        [-2, 1],
        [-2, 3, 4],
        [-3, -4],
        [-3, 2],
        [-4, 2],
        [-1, 5, 6],
        [-5, -6],
        [-5, 1],
        [-6, 1],
        [-7, 6],
    ]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 9
    expected_products = [
        ["A", "C"],
        ["A", "D"],
        ["A", "B", "E", "C"],
        ["A", "B", "E", "D"],
        ["A", "B", "E", "D", "G"],
        ["A", "B", "F", "D", "G"],
        ["A", "B", "F", "D"],
        ["A", "D", "G"],
        ["A", "B", "F", "C"],
    ]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "C": True}),
        Configuration(
            {
                "A": True,
                "B": True,
                "D": True,
                "F": True,
                "G": True,
            }
        ),
    ]
    expected_non_valid_products = [
        Configuration({"A": True}),
        Configuration(
            {
                "A": True,
                "B": True,
                "D": True,
                "E": True,
                "F": True,
                "G": True,
            }
        ),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_optional_or() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "E", 4: "F", 5: "C", 6: "D", 7: "G"}
    model.variables = {"A": 1, "B": 2, "E": 3, "F": 4, "C": 5, "D": 6, "G": 7}
    r_cnf_clauses = [
        [1],
        [-2, 1],
        [-2, 3, 4],
        [-3, 2],
        [-4, 2],
        [-1, 5, 6],
        [-5, 1],
        [-6, 1],
        [-7, 5],
    ]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 20
    expected_products = [
        ["A", "C"],
        ["A", "C", "D"],
        ["A", "C", "D", "G"],
        ["A", "C", "G"],
        ["A", "B", "F", "C", "G"],
        ["A", "B", "E", "F", "C", "G"],
        ["A", "B", "E", "F", "C"],
        ["A", "B", "E", "F", "C", "D"],
        ["A", "B", "E", "C", "D"],
        ["A", "B", "F", "C", "D"],
        ["A", "B", "F", "C", "D", "G"],
        ["A", "B", "F", "D"],
        ["A", "B", "F", "C"],
        ["A", "B", "E", "C"],
        ["A", "B", "E", "C", "G"],
        ["A", "B", "E", "C", "D", "G"],
        ["A", "B", "E", "D"],
        ["A", "B", "E", "F", "D"],
        ["A", "B", "E", "F", "C", "D", "G"],
        ["A", "D"],
    ]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "C": True}),
        Configuration(
            {
                "A": True,
                "B": True,
                "C": True,
                "D": True,
                "E": True,
                "F": True,
                "G": True,
            }
        ),
    ]
    expected_non_valid_products = [Configuration({"A": True})]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_or() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 3
    expected_products = [["A", "B"], ["A", "B", "C"], ["A", "C"]]
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "B": True}),
        Configuration(
            {"A": True, "B": True, "C": True}
        ),
    ]
    expected_non_valid_products = [Configuration({"A": True})]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_or_alternative() -> None:

    model = PySATModel()

    model.features = {
        1: "A",
        2: "B",
        3: "C",
        4: "F",
        5: "G",
        6: "D",
        7: "E",
        8: "H",
        9: "I",
    }
    model.variables = {
        "A": 1,
        "B": 2,
        "C": 3,
        "F": 4,
        "G": 5,
        "D": 6,
        "E": 7,
        "H": 8,
        "I": 9,
    }
    r_cnf_clauses = [
        [1],
        [-1, 2, 3],
        [-2, -3],
        [-2, 1],
        [-3, 1],
        [-2, 4, 5],
        [-4, 2],
        [-5, 2],
        [-1, 6, 7],
        [-6, 1],
        [-7, 1],
        [-7, 8, 9],
        [-8, -9],
        [-8, 7],
        [-9, 7],
    ]
    ctc_cnf_clauses = []
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 20
    expected_products = [
        ["A", "C", "D"],
        ["A", "C", "D", "E", "H"],
        ["A", "C", "D", "E", "I"],
        ["A", "B", "F", "D", "E", "I"],
        ["A", "B", "F", "G", "D", "E", "I"],
        ["A", "B", "F", "G", "D"],
        ["A", "B", "G", "D"],
        ["A", "B", "G", "D", "E", "I"],
        ["A", "B", "F", "D"],
        ["A", "B", "F", "E", "I"],
        ["A", "B", "F", "E", "H"],
        ["A", "B", "F", "D", "E", "H"],
        ["A", "C", "E", "H"],
        ["A", "C", "E", "I"],
        ["A", "B", "G", "E", "I"],
        ["A", "B", "F", "G", "E", "I"],
        ["A", "B", "F", "G", "D", "E", "H"],
        ["A", "B", "F", "G", "E", "H"],
        ["A", "B", "G", "E", "H"],
        ["A", "B", "G", "D", "E", "H"],
    ]
    #This is a tranlation of the expected products to Configuration objects
    expected_products = [
        Configuration({feature: True for feature in string_list})
            for string_list in expected_products
    ]
    expected_valid = True
    expected_valid_products = [
        Configuration(
            {"A": True, "C": True, "D": True}
        ),
        Configuration(
            {
                "A": True,
                "B": True,
                "D": True,
                "E": True,
                "F": True,
                "G": True,
                "H": True,
            }
        ),
    ]
    expected_non_valid_products = [
        Configuration({"A": True, "C": True}),
        Configuration(
            {
                "A": True,
                "B": True,
                "D": True,
                "E": True,
                "F": True,
                "G": True,
                "H": True,
                "I": True,
            }
        ),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_or_excludes() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-2, -3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = None
    expected_products = None
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True, "B": True})
    ]
    expected_non_valid_products = [
        Configuration({"A": True}),
        Configuration(
            {"A": True, "B": True, "C": True}
        ),
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_or_requires() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-1, 2, 3], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-2, 3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [
        Configuration( {"A": True, "B": True, "C": True}), 
        Configuration({"A": True, "C": True},)
                      ]
    expected_valid = True
    expected_valid_products = [
        Configuration(
            {"A": True, "C": True},
        ),
        Configuration(
            {"A": True, "B": True, "C": True}
        ),
    ]
    expected_non_valid_products = [Configuration({"A": True})]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_requires() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-2, 3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 3
    expected_products = [Configuration({"A":True}), 
                         Configuration({"A":True, "C":True}), 
                         Configuration({"A":True, "B":True, "C":True})]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True}),
        Configuration(
            {"A": True, "B": True, "C": True}
        ),
    ]
    expected_non_valid_products = None

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )


def test_relationships_requires_excludes() -> None:

    model = PySATModel()

    model.features = {1: "A", 2: "B", 3: "C"}
    model.variables = {"A": 1, "B": 2, "C": 3}
    r_cnf_clauses = [[1], [-2, 1], [-3, 1]]
    ctc_cnf_clauses = [[-2, 3], [-2, -3]]
    for clause in r_cnf_clauses:
        model.add_clause(clause)
    for clause in ctc_cnf_clauses:
        model.add_clause(clause)

    expected_core_features = None
    expected_dead_features = None
    expected_error_detection = None
    expected_error_diagnosis = None
    expected_false_optional_features = None
    expected_products_number = 2
    expected_products = [Configuration({"A": True}), Configuration({"A": True, "C":True})]
    expected_valid = True
    expected_valid_products = [
        Configuration({"A": True}),
        Configuration({"A": True, "C": True}),
    ]
    expected_non_valid_products = [
        Configuration(
            {"A": True, "B": True, "C": True}
        )
    ]

    run(
        model,
        expected_core_features,
        expected_dead_features,
        expected_error_detection,
        expected_error_diagnosis,
        expected_false_optional_features,
        expected_products_number,
        expected_products,
        expected_valid,
        expected_valid_products,
        expected_non_valid_products,
    )
