"""The CNF encoding the SAT builders use by default: 'auto' since 2.9 (distributive clauses for
every constraint whose expansion stays small, Tseytin for the ones that blow up)."""
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_diagnosis_metamodel.transformations import FmToDiagPysat
from flamapy.metamodels.pysat_metamodel.operations import PySATConfigurationsNumber
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat

_LEAVES = ''.join(f'            {name}\n' for name in ['A', 'B', 'C', 'D', 'E', 'F'])


def _model(tmp_path, constraints: str):
    src = tmp_path / 'model.uvl'
    src.write_text(f'features\n    R\n        optional\n{_LEAVES}constraints\n{constraints}')
    return UVLReader(str(src)).transform()


def test_default_is_auto_and_matches_distributive_on_simple_constraints(tmp_path) -> None:
    fm = _model(tmp_path, '    A => B\n    !(E & F)\n')
    default = FmToPysat(fm).transform()
    assert default.cnf_method == 'auto'
    assert not default.auxiliary_variables
    distributive = FmToPysat(fm, cnf_method='distributive').transform()
    assert default.get_all_clauses().clauses == distributive.get_all_clauses().clauses


def test_default_switches_to_tseytin_only_where_the_expansion_blows_up(tmp_path) -> None:
    fm = _model(tmp_path, '    A => B\n    (A & B & C) | (D & E & F) | (A & D) | (B & E)\n')
    default = FmToPysat(fm).transform()
    distributive = FmToPysat(fm, cnf_method='distributive').transform()
    assert default.auxiliary_variables
    assert len(default.get_all_clauses().clauses) < len(distributive.get_all_clauses().clauses)
    counts = {PySATConfigurationsNumber().execute(model).get_result()
              for model in (default, distributive)}
    assert len(counts) == 1  # the auxiliaries are projected out of every result


def test_diagnosis_builder_shares_the_default(tmp_path) -> None:
    fm = _model(tmp_path, '    (A & B & C) | (D & E & F) | (A & D) | (B & E)\n')
    assert FmToDiagPysat(fm).cnf_method == 'auto'
