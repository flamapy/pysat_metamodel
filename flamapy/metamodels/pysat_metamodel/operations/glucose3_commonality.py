from flamapy.core.operations import Commonality
from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products


class Glucose3Commonality(Commonality):
    def __init__(self) -> None:
        self.commonality: float = 0
        self.configuration = Configuration({})

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def get_commonality(self) -> float:
        return self.commonality

    def get_result(self) -> float:
        return self.get_commonality()

    def execute(self, model: VariabilityModel) -> 'Glucose3Commonality':
        glucose3products = Glucose3Products()
        glucose3products.execute(model)

        products = glucose3products.get_result()

        feature = list(self.configuration.elements.keys())[0]

        count = 0
        for product in products:
            count = count + \
                1 if feature.name in product else count

        self.commonality = count / len(products)

        return self
