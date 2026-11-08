from flamapy.core.manifest import OperationCapability, PluginManifest
from flamapy.core.models.language_level import LanguageLevel, MajorLevel, MinorLevel

# Costs are estimated milliseconds from the 2026-11-06 calibration (betty synthetic models at 1%
# and 30% constraint density, 20-10,000 features, plus JHipster and busybox; worst case of the
# two densities, carried forward so a curve never decreases). SAT queries scale to the largest
# models (satisfiable 8 ms, core/dead 70 ms and false-optional 300 ms at 10,000 features), so the
# only limits are on the operations that enumerate every configuration.
_SAT_QUERY = ((2000, 1), (5000, 4), (10000, 8))
_IMPLICATION_QUERIES = ((1000, 2), (2000, 4), (5000, 40), (10000, 70))

MANIFEST = PluginManifest(
    name='pysat',
    calibration='2026-11-06',
    extension='pysat',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, {MinorLevel.GROUP_CARDINALITY}),
    transformation_cost_curve=((200, 1), (1000, 4), (2000, 12), (5000, 19), (10000, 46)),
    operations={
        'satisfiable': OperationCapability(cost_curve=_SAT_QUERY),
        'satisfiable_configuration': OperationCapability(cost_curve=_SAT_QUERY),
        'core_features': OperationCapability(cost_curve=_IMPLICATION_QUERIES),
        'dead_features': OperationCapability(cost_curve=_IMPLICATION_QUERIES),
        'false_optional_features': OperationCapability(
            cost_curve=((500, 2), (1000, 6), (2000, 34), (5000, 110), (10000, 300))),
        # Atomic sets: the classes of features with the same value in every configuration,
        # proved with grouped implication queries like the backbone.
        'atomic_sets': OperationCapability(cost_curve=_IMPLICATION_QUERIES),
        'minimum_configuration': OperationCapability(
            cost_curve=((200, 2), (1000, 5), (2000, 30), (5000, 38), (10000, 110))),
        # Pairwise sampling (the only t-wise implementation): 1.2 s at 200 features, 56 s at
        # 500, 6.5 min at 1,000; the 2,000-feature model did not finish within 10 minutes.
        't_wise_sampling': OperationCapability(
            cost_curve=((50, 100), (100, 310), (200, 1200), (500, 56000), (1000, 390000),
                        (2000, 600000))),
        # PySATSampling returns valid configurations, so its results are exact; it enumerates
        # them deterministically rather than uniformly (BDD sampling, the default backend, is
        # uniform), which the cost and the default-backend bonus already account for.
        'sampling': OperationCapability(cost_curve=((1000, 1), (5000, 9), (10000, 15))),
        # Counting and listing enumerate every configuration: exponential in the number of
        # configurations rather than in the features (6 ms on the 20-feature calibration model).
        'configurations_number': OperationCapability(max_features=30, cost=400),
        'configurations': OperationCapability(max_features=30, cost=400),
        'commonality': OperationCapability(max_features=30, cost=400),
    },
)
