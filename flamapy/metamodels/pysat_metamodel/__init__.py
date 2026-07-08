from flamapy.core.manifest import PluginManifest, OperationCapability
from flamapy.core.models.language_level import LanguageLevel, MajorLevel

# Costs/limits from the 2.8 calibration run (2026-07-09): SAT queries scale well
# (satisfiable 1.2ms and core/dead ~14ms at 500 features), but counting/enumeration
# enumerates every configuration and already timed out at 50 features.
MANIFEST = PluginManifest(
    name='pysat',
    extension='pysat',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, set()),
    operations={
        'configurations_number': OperationCapability(max_features=30, cost=400),
        'configurations': OperationCapability(max_features=30, cost=400),
    },
)
