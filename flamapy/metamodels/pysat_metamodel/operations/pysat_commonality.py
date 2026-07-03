from flamapy.core.operations import Commonality
from flamapy.core.operations.descriptor import OperationDescriptor, Input
from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from .pysat_configurations import PySATConfigurations


class PySATCommonality(Commonality):
    facade = OperationDescriptor(
        doc=(
            'This is a measure of how often a feature appears in the products of a product\n'
            "line. It's usually expressed as a percentage. A feature with 100 per cent\n"
            'commonality is a core feature, as it appears in all products.\n'
            '\n'
            '``configuration_path`` accepts a configuration file path, a ``{feature:\n'
            'value}`` mapping, or a Configuration object.'
        ),
        returns='Union[None, float]',
        name='commonality', operation='PySATCommonality', default_backend='sat',
        inputs=(Input('configuration_path', str, required=True, kind='configuration',
                      setter='set_configuration'),),
    )

    def __init__(self) -> None:
        self.result: float = 0
        self.configuration = Configuration({})

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def get_commonality(self) -> float:
        return self.get_result()

    def get_result(self) -> float:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATCommonality':
        pysat_products_op = PySATConfigurations()
        pysat_products_op.execute(model)
        products = pysat_products_op.get_result()

        feature = next(iter(self.configuration.elements.keys()))

        count = 0
        for product in products:
            count = count + 1 if feature in product else count

        self.result = count / len(products)

        return self
