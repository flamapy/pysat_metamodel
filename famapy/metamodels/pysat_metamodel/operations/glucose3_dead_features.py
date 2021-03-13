from famapy.core.operations import DeadFeatures
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products


class Glucose3DeadFeatures(DeadFeatures):

    def __init__(self):
        self.dead_features = []
        self.products = None

    def get_dead_features(self):
        return self.dead_features

    def get_result(self):
        return self.get_dead_features()

    def set_products(self, products: list):
        self.products = products

    def set_up(self, model: PySATModel, have_products):
        if not have_products:
            products = Glucose3Products()
            products.execute(model)
            products = products.get_products()
            self.products = products

    def execute(self, model: PySATModel) -> 'Glucose3DeadFeatures':
        self.set_up(model, self.products is not None)

        dead_features = model.variables
        for product in self.products:
            aux = []
            for feat in dead_features:
                if feat not in product:
                    aux.append(feat)
            dead_features = [feat for feat in dead_features if feat in aux]

        self.dead_features=dead_features
        return self
