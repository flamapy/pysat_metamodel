from famapy.core.models import Configuration


class PySATConfiguration(Configuration):

    def __init__(self, elements: dict) -> None:  # make elements to be a dict of feature, boolean
        self.elements = elements
