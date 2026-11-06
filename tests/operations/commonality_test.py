"""Commonality of partial and full configurations against exhaustive enumeration."""
import os
import random
import tempfile

import pytest
from pysat.solvers import Solver

from flamapy.core.exceptions import FlamaException
from flamapy.core.operations import Commonality
from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel import MANIFEST
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import PySATCommonality


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
constraints
    Camera => HighRes
    Unreachable => !Root
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


def _configurations(sat):
    with Solver(name='glucose3', bootstrap_with=sat.get_all_clauses().clauses) as solver:
        return [frozenset(sat.selected_features(model)) for model in solver.enum_models()]


def _commonality(sat, configuration):
    operation = PySATCommonality()
    operation.set_configuration(configuration)
    return operation.execute(sat).get_result()


def _expected(configs, decided, full=False):
    def includes(config):
        return all((name in config) == selected for name, selected in decided.items()) and \
            (not full or config <= set(decided))
    return sum(1 for c in configs if includes(c)) / len(configs) if configs else 0.0


@pytest.mark.parametrize('seed', range(40))
def test_partial_configurations_match_enumeration(seed):
    fm = _read(_random_model(seed))
    sat = FmToPysat(fm, cnf_method='tseytin' if seed % 2 else 'distributive').transform()
    configs = _configurations(sat)
    rnd = random.Random(seed)
    names = [f.name for f in fm.get_features()]
    for size in (1, 2, 4):
        decided = {name: rnd.random() < 0.5 for name in rnd.sample(names, size)}
        assert _commonality(sat, Configuration(dict(decided))) == \
            pytest.approx(_expected(configs, decided))


def test_single_features_are_the_commonality_factors():
    sat = FmToPysat(_read(SMARTWATCH)).transform()
    configs = _configurations(sat)
    assert _commonality(sat, Configuration({'Core': True})) == 1.0        # core
    assert _commonality(sat, Configuration({'Unreachable': True})) == 0.0  # dead
    assert _commonality(sat, Configuration({'Camera': True})) == \
        pytest.approx(sum(1 for c in configs if 'Camera' in c) / len(configs))
    # deselecting a feature counts the configurations without it
    assert _commonality(sat, Configuration({'Camera': False})) == \
        pytest.approx(sum(1 for c in configs if 'Camera' not in c) / len(configs))
    # a configuration the constraints forbid has no products
    assert _commonality(sat, Configuration({'Camera': True, 'HighRes': False})) == 0.0


def test_full_configuration_counts_one_product():
    sat = FmToPysat(_read(SMARTWATCH)).transform()
    configs = _configurations(sat)
    product = Configuration({name: True for name in ('Root', 'Core', 'Screen', 'Analog')})
    product.set_full(True)
    assert _commonality(sat, product) == pytest.approx(1 / len(configs))
    partial = Configuration({name: True for name in ('Root', 'Core', 'Screen', 'Analog')})
    assert _commonality(sat, partial) == \
        pytest.approx(sum(1 for c in configs if 'Analog' in c) / len(configs))
    not_a_product = Configuration({'Root': True, 'Core': True})   # Screen is mandatory
    not_a_product.set_full(True)
    assert _commonality(sat, not_a_product) == 0.0


def test_void_model_has_commonality_zero():
    sat = FmToPysat(_read(VOID)).transform()
    assert _commonality(sat, Configuration({'A': True})) == 0.0
    assert _commonality(sat, Configuration({})) == 0.0


def test_unknown_feature_is_an_error():
    sat = FmToPysat(_read(SMARTWATCH)).transform()
    with pytest.raises(FlamaException, match='Missing'):
        _commonality(sat, Configuration({'Missing': True}))


def test_descriptor_and_manifest():
    assert PySATCommonality.facade is Commonality.facade
    assert Commonality.facade.name == 'commonality'
    assert Commonality.facade.selectable_backend
    assert MANIFEST.operations['commonality'].max_features == 30   # enumerates the products
