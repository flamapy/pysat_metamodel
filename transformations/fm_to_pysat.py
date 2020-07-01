from core.models.VariabilityModel import VariabilityModel
from core.transformations.ModelToModel import ModelToModelTransformation
from fm_metamodel.model.FeatureModel import Feature, FeatureModel, Relation

class Fm_to_pysat(ModelToModelTransformation):
    def __init__(self, model1: VariabilityModel, model2: VariabilityModel): # TODO: Here we should type this properly fm and sat
        self.counter = 1
        self.model1 = model1
        self.model2 = model2
        self.cnf = model2.cnf

    def add_feature(self, feature):
        if not feature.name in self.model2.variables.keys():
            self.model2.variables[feature.name] = self.counter
            self.model2.features[self.counter] = feature.name

            self.counter += 1

    def add_root(self, feature):
         self.cnf.append([self.model2.variables.get(feature.name)])

    def add_relation(self, relation):
        if (relation.isMandatory()):
            self.cnf.append([-1 * self.model2.variables.get(relation.parent.name),
                    self.model2.variables.get(relation.children[0].name)])
            self.cnf.append([-1 * self.model2.variables.get(relation.children[0].name),
                    self.model2.variables.get(relation.parent.name)])

        elif (relation.isOptional()):
            self.cnf.append([-1 * self.model2.variables.get(relation.children[0].name),
                    self.model2.variables.get(relation.parent.name)])


        elif (relation.isSet()):
            pass
        elif (relation.isAlternate()):
            pass
        else:
            pass
        
    def transform(self):
        for feature in self.model1.get_features():
            self.add_feature(feature)

        self.add_root(self.model1.root)

        for relation in self.model1.get_relations():
            self.add_relation(relation)