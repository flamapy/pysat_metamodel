from flamapy.core.manifest import PluginManifest
from flamapy.core.models.language_level import LanguageLevel, MajorLevel

MANIFEST = PluginManifest(
    name='pysat',
    extension='pysat',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, set()),
)
