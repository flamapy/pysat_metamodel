from flamapy.core.manifest import PluginManifest
from flamapy.core.models.language_level import LanguageLevel, MajorLevel, MinorLevel

MANIFEST = PluginManifest(
    name='pysat_diagnosis',
    extension='pysat_diagnosis',
    # Same encoder as the SAT plugin (ClauseSet), so the same language level.
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, {MinorLevel.GROUP_CARDINALITY}),
)
