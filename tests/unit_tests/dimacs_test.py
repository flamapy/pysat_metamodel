"""DIMACS export and import of SAT models with Tseytin auxiliary variables."""
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.operations import PySATConfigurationsNumber
from flamapy.metamodels.pysat_metamodel.transformations import (
    DimacsReader,
    DimacsWriter,
    FmToPysat,
)

UVL = '''features
    R
        optional
            A
            B
            C
            D
constraints
    (A & B) | (C & D)
'''


def _count(model) -> int:
    return PySATConfigurationsNumber().execute(model).get_result()


def test_header_counts_auxiliary_variables_and_reads_back(tmp_path) -> None:
    source = tmp_path / 'model.uvl'
    source.write_text(UVL)
    sat = FmToPysat(UVLReader(str(source)).transform(), cnf_method='tseytin').transform()
    assert sat.auxiliary_variables
    path = tmp_path / 'model.dimacs'
    text = DimacsWriter(str(path), sat).transform()
    header = next(line for line in text.splitlines() if line.startswith('p cnf'))
    assert int(header.split()[2]) == sat.top_variable()
    assert len([line for line in text.splitlines() if line.startswith('c ')]) == len(sat.features)

    back = DimacsReader(str(path)).transform()
    assert back.auxiliary_variables == sat.auxiliary_variables
    assert back.cnf_method is None
    assert _count(back) == _count(sat)
