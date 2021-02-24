from famapy.core.models import Configuration


class Configuration(Configuration):

    def __init__(self, elements: dict) -> bool:  # make elements to be a dict of feature, boolean
        self.elements = elements