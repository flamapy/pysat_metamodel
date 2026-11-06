"""The SAT metrics: values equal to the operations they summarize, with one backbone computation
and at most one enumeration of the configurations per run."""
import os
import tempfile

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import (
    PySATBackbone,
    PySATConfigurations,
    PySATFalseOptionalFeatures,
    PySATMetrics,
)

MODEL = '''features
    Root
        mandatory
            Core
        optional
            Camera
            GPS
            Unreachable
            Always
            NeedsParent
                optional
                    Child
constraints
    Unreachable => !Root
    Core => Always
    NeedsParent => Child
'''


def _sat_model():
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(MODEL)
        return FmToPysat(UVLReader(path).transform()).transform()
    finally:
        os.remove(path)


def test_metrics_match_the_operations():
    sat_model = _sat_model()
    metrics = {m['name']: m for m in PySATMetrics().calculate_metamodel_metrics(sat_model)}
    backbone = PySATBackbone().execute(sat_model).get_result()
    assert metrics['Core features']['result'] == backbone['core']
    assert metrics['Dead features']['result'] == backbone['dead'] == ['Unreachable']
    assert metrics['Variant features']['result'] == [
        f for f in sat_model.features.values()
        if f not in backbone['core'] and f not in backbone['dead']]
    assert metrics['False-optional features']['result'] == \
        PySATFalseOptionalFeatures().execute(sat_model).get_result() == ['Always', 'Child']
    configurations = PySATConfigurations().execute(sat_model).get_result()
    assert metrics['Configurations']['size'] == len(configurations) == 8
    seen = {}
    for configuration in configurations:
        for feature in configuration.get_selected_elements():
            seen[feature] = seen.get(feature, 0) + 1
    assert sorted(metrics['Unique features']['result']) == \
        sorted(f for f, n in seen.items() if n == 1)


def test_backbone_once_and_configurations_once(monkeypatch):
    sat_model = _sat_model()
    calls = {'backbone': 0, 'configurations': 0}
    backbone_execute = PySATBackbone.execute
    configurations_execute = PySATConfigurations.execute

    def counting_backbone(self, model):
        calls['backbone'] += 1
        return backbone_execute(self, model)

    def counting_configurations(self, model):
        calls['configurations'] += 1
        return configurations_execute(self, model)

    monkeypatch.setattr(PySATBackbone, 'execute', counting_backbone)
    monkeypatch.setattr(PySATConfigurations, 'execute', counting_configurations)
    PySATMetrics().calculate_metamodel_metrics(sat_model)
    assert calls == {'backbone': 1, 'configurations': 1}
