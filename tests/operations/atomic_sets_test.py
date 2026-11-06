"""Exact atomic sets (the classes of features with the same value in every configuration)
against exhaustive enumeration and against the tree-only operation."""
import os
import random
import tempfile

import pytest
from pysat.solvers import Solver

from flamapy.core.operations import AtomicSets
from flamapy.metamodels.fm_metamodel.operations import FMAtomicSets
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel import MANIFEST
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import PySATAtomicSets, pysat_atomic_sets


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
constraints
    A => B
    B => !A
'''

TREE_ONLY = '''features
    Root
        mandatory
            A
                mandatory
                    A1
                optional
                    A2
            B
                alternative
                    B1
                    B2
        optional
            C
                mandatory
                    C1
                    C2
                or
                    D1
                    D2
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
    """The classes of features with the same value in every configuration, by enumeration."""
    with Solver(name='glucose3', bootstrap_with=sat.get_all_clauses().clauses) as solver:
        configs = [frozenset(sat.selected_features(model)) for model in solver.enum_models()]
    if not configs:
        return []
    classes = {}
    for feature in fm.get_features():
        signature = tuple(feature.name in config for config in configs)
        classes.setdefault(signature, set()).add(feature.name)
    return sorted(sorted(c) for c in classes.values())


def _atomic_sets(sat):
    return PySATAtomicSets().execute(sat).get_result()


def _check(uvl, cnf_method='distributive'):
    fm = _read(uvl)
    sat = FmToPysat(fm, cnf_method=cnf_method).transform()
    result = _atomic_sets(sat)
    assert all(isinstance(atomic_set, set) for atomic_set in result)
    assert sorted(sorted(s) for s in result) == _expected(fm, sat)
    return result


@pytest.mark.parametrize('cnf_method', ['distributive', 'tseytin'])
def test_smartwatch_like_model(cnf_method):
    result = _check(SMARTWATCH, cnf_method)
    assert result[0] == {'Root', 'Core', 'Screen', 'Always'}   # the core features, first
    assert {'NeedsParent', 'Child'} in result                   # merged by a constraint
    assert {'Unreachable'} in result                            # the dead features
    assert {'Camera'} in result and {'HighRes'} in result       # implied, not equivalent


@pytest.mark.parametrize('seed', range(40))
def test_random_models_match_enumeration(seed):
    _check(_random_model(seed), 'tseytin' if seed % 2 else 'distributive')


def test_tree_only_model_equals_the_structural_operation():
    fm = _read(TREE_ONLY)
    structural = {frozenset(f.name for f in s) for s in FMAtomicSets().execute(fm).get_result()}
    exact = {frozenset(s) for s in _atomic_sets(FmToPysat(fm).transform())}
    assert exact == structural


def test_dead_features_form_one_class():
    uvl = '''features
    Root
        optional
            A
                optional
                    A1
            B
constraints
    !A
'''
    result = _check(uvl)
    assert {'A', 'A1'} in result


def test_void_model_has_no_atomic_sets():
    assert _atomic_sets(FmToPysat(_read(VOID)).transform()) == []


SOLVERS = ['glucose3', 'glucose4', 'minisat22', 'lingeling', 'maplesat', 'cadical153']


@pytest.mark.parametrize('solver_name', SOLVERS)
def test_every_pysat_solver(solver_name, monkeypatch):
    from pysat.solvers import Solver as PySATSolver

    def factory(*args, **kwargs):
        kwargs['name'] = solver_name
        return PySATSolver(*args, **kwargs)

    monkeypatch.setattr(pysat_atomic_sets, 'Solver', factory)
    for seed in range(4):
        _check(_random_model(seed))
    _check(SMARTWATCH, 'tseytin')


def test_descriptor_and_manifest():
    assert PySATAtomicSets.facade is AtomicSets.facade
    assert AtomicSets.facade.name == 'atomic_sets'
    assert AtomicSets.facade.result_adapter([{'A'}]) == [['A']]
    assert MANIFEST.operations['atomic_sets'].exact
    assert MANIFEST.operations['atomic_sets'].cost_curve
