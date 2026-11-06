"""Core, dead and false-optional features against exhaustive enumeration.

The SAT implementations prune candidates with solver models and prove the remaining candidates in
grouped calls; these tests check that the answers equal the definitions computed by enumerating
every configuration, with both CNF encodings, on satisfiable and void models.
"""
import os
import random
import tempfile

import pytest
from pysat.solvers import Solver

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import (
    PySATBackbone,
    PySATCoreFeatures,
    PySATDeadFeatures,
    PySATFalseOptionalFeatures,
)


def _read(uvl):
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(uvl)
        return UVLReader(path).transform()
    finally:
        os.remove(path)


SMARTWATCH = '''features
    Root
        mandatory
            Core
            Screen
                alternative
                    Analog
                    HighRes
                    EInk
        optional
            Connector
                or
                    USB
                    Wireless
                    Bluetooth
            Camera
            GPS
            Unreachable
            Always
            NeedsParent
                optional
                    Child
constraints
    Camera => HighRes
    Unreachable => !Root
    Core => Always
    NeedsParent => Child
    GPS => Connector
'''

VOID = '''features
    Root
        mandatory
            A
        optional
            B
            C
constraints
    A => B
    B => !A
'''


def _random_model(seed, n_features=10, n_constraints=6):
    rnd = random.Random(seed)
    names = [f'F{i}' for i in range(n_features)]
    lines = ['features', '    Root', '        optional']
    lines += [f'            {n}' for n in names[:n_features // 2]]
    lines += ['        mandatory', '            M', '                optional']
    lines += [f'                    {n}' for n in names[n_features // 2:]]
    lines.append('constraints')
    for _ in range(n_constraints):
        left, right = rnd.sample(names, 2)
        template = rnd.choice(['{} => {}', '{} => !{}', '!{} => {}', '{} | {}', '{} <=> {}'])
        lines.append('    ' + template.format(left, right))
    return '\n'.join(lines) + '\n'


def _expected(fm, sat):
    """Definitions by enumeration of every configuration (projected on the features)."""
    with Solver(name='glucose3', bootstrap_with=sat.get_all_clauses().clauses) as solver:
        configs = {frozenset(sat.selected_features(model)) for model in solver.enum_models()}
    names = [f.name for f in fm.get_features()]
    core = [n for n in names if all(n in c for c in configs)]
    dead = [n for n in names if not any(n in c for c in configs)]
    false_optional = []
    for f in fm.get_features():
        if f.is_root() or f.is_mandatory() or f.get_parent() is None:
            continue
        with_parent = [c for c in configs if f.get_parent().name in c]
        if all(f.name in c for c in with_parent):
            false_optional.append(f.name)
    return core, dead, false_optional, len(configs)


def _check(uvl, cnf_method):
    fm = _read(uvl)
    sat = FmToPysat(fm, cnf_method=cnf_method).transform()
    core, dead, false_optional, n_configs = _expected(fm, sat)
    assert sorted(PySATCoreFeatures().execute(sat).get_result()) == sorted(core)
    assert sorted(PySATDeadFeatures().execute(sat).get_result()) == sorted(dead)
    assert sorted(PySATFalseOptionalFeatures().execute(sat).get_result()) == sorted(false_optional)
    backbone = PySATBackbone().execute(sat).get_result()
    assert sorted(backbone['core']) == sorted(core) and sorted(backbone['dead']) == sorted(dead)
    return n_configs


@pytest.mark.parametrize('cnf_method', ['distributive', 'tseytin'])
def test_smartwatch_like_model(cnf_method):
    fm = _read(SMARTWATCH)
    sat = FmToPysat(fm, cnf_method=cnf_method).transform()
    assert PySATCoreFeatures().execute(sat).get_result() == ['Root', 'Core', 'Screen', 'Always']
    assert PySATDeadFeatures().execute(sat).get_result() == ['Unreachable']
    # Always is implied by the root, Child by its (optional) parent: both false optional
    assert PySATFalseOptionalFeatures().execute(sat).get_result() == ['Always', 'Child']
    _check(SMARTWATCH, cnf_method)


@pytest.mark.parametrize('cnf_method', ['distributive', 'tseytin'])
def test_void_model_keeps_the_vacuous_convention(cnf_method):
    sat = FmToPysat(_read(VOID), cnf_method=cnf_method).transform()
    assert PySATCoreFeatures().execute(sat).get_result() == []
    assert PySATDeadFeatures().execute(sat).get_result() == ['Root', 'A', 'B', 'C']
    assert PySATFalseOptionalFeatures().execute(sat).get_result() == ['B', 'C']


@pytest.mark.parametrize('seed', range(40))
def test_random_models_match_enumeration(seed):
    uvl = _random_model(seed)
    n_distributive = _check(uvl, 'distributive')
    n_tseytin = _check(uvl, 'tseytin')
    assert n_distributive == n_tseytin


def test_results_keep_the_model_order():
    uvl = _random_model(7, n_features=12, n_constraints=10)
    fm = _read(uvl)
    sat = FmToPysat(fm).transform()
    order = {f.name: i for i, f in enumerate(fm.get_features())}
    for operation in (PySATCoreFeatures(), PySATDeadFeatures(), PySATFalseOptionalFeatures()):
        result = operation.execute(sat).get_result()
        assert result == sorted(result, key=order.__getitem__)


SOLVERS = ['glucose3', 'glucose4', 'minisat22', 'lingeling', 'maplesat', 'cadical153']


@pytest.mark.parametrize('solver_name', SOLVERS)
def test_every_pysat_solver(solver_name, monkeypatch):
    """The operations hard-code glucose3; tools (and the benchmark) rebind `Solver` to pick another
    PySAT solver. CaDiCaL drops the last model when a clause is added and aborts the process if
    it is read afterwards, so the order of the calls matters."""
    from pysat.solvers import Solver as PySATSolver
    from flamapy.metamodels.pysat_metamodel.operations import (
        pysat_backbone,
        pysat_false_optional_features,
    )

    def factory(*args, **kwargs):
        kwargs['name'] = solver_name
        return PySATSolver(*args, **kwargs)

    monkeypatch.setattr(pysat_backbone, 'Solver', factory)
    monkeypatch.setattr(pysat_false_optional_features, 'Solver', factory)
    for seed in range(6):
        _check(_random_model(seed), 'distributive')
    _check(SMARTWATCH, 'tseytin')
    void = FmToPysat(_read(VOID)).transform()
    assert PySATCoreFeatures().execute(void).get_result() == []
    assert PySATDeadFeatures().execute(void).get_result() == ['Root', 'A', 'B', 'C']
    assert PySATFalseOptionalFeatures().execute(void).get_result() == ['B', 'C']
