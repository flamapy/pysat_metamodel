from famapy.core.models import Configuration
from famapy.metamodels.fm_metamodel.models.feature_model import Feature

from typing import Dict


class PySATConfiguration(Configuration):

    def __init__(self, elements: Dict[Feature, bool]) -> bool:  # make elements to be a dict of feature, boolean
        self.elements = elements