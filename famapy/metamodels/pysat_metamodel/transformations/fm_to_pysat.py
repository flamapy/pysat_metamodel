import sys

from famapy.core.models.VariabilityModel import VariabilityModel
from famapy.core.transformations.ModelToModel import ModelToModel
from famapy.metamodels.pysat_metamodel.models.PySATModel import PySATModel


class Fm_to_pysat(ModelToModel):
    EXT_SRC = 'fm'
    EXT_DST = 'pysat'

    def __init__(self, model_src: VariabilityModel):
        super().__init__(model_src)
        self.counter = 1
        self.model_dst = PySATModel()
        self.cnf = self.model_dst.cnf

    def add_feature(self, feature):
        if not feature.name in self.model_dst.variables.keys():
            self.model_dst.variables[feature.name] = self.counter
            self.model_dst.features[self.counter] = feature.name
            self.counter += 1

    def add_root(self, feature):
         self.cnf.append([self.model_dst.variables.get(feature.name)])

    def add_relation(self, relation):
        if (relation.is_mandatory()):
            self.cnf.append([-1 * self.model_dst.variables.get(relation.parent.name),
                    self.model_dst.variables.get(relation.children[0].name)])
            self.cnf.append([-1 * self.model_dst.variables.get(relation.children[0].name),
                    self.model_dst.variables.get(relation.parent.name)])

        elif (relation.is_optional()):
            self.cnf.append([-1 * self.model_dst.variables.get(relation.children[0].name),
                    self.model_dst.variables.get(relation.parent.name)])


        elif (relation.is_or()):#this is a 1 to n relatinship with multiple childs

             #add the first cnf 	child1 or child2 or ... or childN or no parent)
            alt_cnf=[-1*self.model_dst.variables.get(relation.parent.name)] #first elem of the constraint
            for child in relation.children :
                alt_cnf.append(self.model_dst.variables.get(child.name))
            self.cnf.append(alt_cnf)

            for child in relation.children:
                self.cnf.append([-1*self.model_dst.variables.get(child.name),self.model_dst.variables.get(relation.parent.name)])

        elif (relation.is_alternative()): #this is a 1 to 1 relatinship with multiple childs

            #add the first cnf 	child1 or child2 or ... or childN or no parent)
            alt_cnf=[-1*self.model_dst.variables.get(relation.parent.name)] #first elem of the constraint
            for child in relation.children :
                alt_cnf.append(self.model_dst.variables.get(child.name))
            self.cnf.append(alt_cnf)

            for i in range(len(relation.children)):
                for j in range(i+1,len(relation.children)):
                    if i!=j:
                        self.cnf.append([-1*self.model_dst.variables.get(relation.children[i].name),-1*self.model_dst.variables.get(relation.children[j].name)])
                self.cnf.append([-1*self.model_dst.variables.get(relation.children[i].name),self.model_dst.variables.get(relation.parent.name)])


        else: #This is a m to n relationship
            print("fatal error. N to M relationships are not yet supported in PySAT", file=sys.stderr)

    def transform(self):
        for feature in self.model_src.get_features():
            self.add_feature(feature)

        self.add_root(self.model_src.root)

        for relation in self.model_src.get_relations():
            self.add_relation(relation)
        return super().transform()
