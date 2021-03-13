from famapy.core.operations import CoreFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products


class Glucose3CoreFeatures(CoreFeatures):

    def __init__(self):
        self.core_features = []
        self.products = None

    def get_core_features(self):
        return self.core_features

    def get_result(self):
        return self.get_core_features()

    def set_products(self, products: list):
        self.products = products

    def set_up(self, model: PySATModel, have_products):
        if not have_products:
            products = Glucose3Products()
            products.execute(model)
            products = products.get_products()
            self.products = products

    def execute(self, model: PySATModel) -> 'Glucose3CoreFeatures':
        self.set_up(model, self.products is not None)

        core_features = model.variables
        for product in self.products:
            aux = []
            for feat in core_features:
                if feat not in product:
                    aux.append(feat)
            core_features = [feat for feat in core_features if feat not in aux]

        self.core_features=core_features
        return self
