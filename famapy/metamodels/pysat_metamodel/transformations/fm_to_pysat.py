import sys
import copy
from typing import Any

from famapy.core.models import VariabilityModel
from famapy.core.transformations import ModelToModel
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class FmToPysat(ModelToModel):
    @staticmethod
    def get_source_extension():
        return 'fm'

    @staticmethod
    def get_destination_extension():
        return 'pysat'

    def __init__(self, source_model: VariabilityModel):
        self.source_model = source_model
        self.counter = 1
        self.destination_model = PySATModel()
        self.r_cnf = self.destination_model.r_cnf
        self.ctc_cnf = self.destination_model.ctc_cnf

    def add_feature(self, feature):
        if feature.name not in self.destination_model.variables.keys():
            self.destination_model.variables[feature.name] = self.counter
            self.destination_model.features[self.counter] = feature.name
            self.counter += 1

    def add_root(self, feature):
        self.r_cnf.append([self.destination_model.variables.get(feature.name)])

    def add_relation(self, relation):  # noqa: MC0001
        if relation.is_mandatory():
            self.r_cnf.append([
                -1 * self.destination_model.variables.get(relation.parent.name),
                self.destination_model.variables.get(relation.children[0].name)])
            self.r_cnf.append([
                -1 * self.destination_model.variables.get(relation.children[0].name),
                self.destination_model.variables.get(relation.parent.name)])

        elif relation.is_optional():
            self.r_cnf.append([
                -1 * self.destination_model.variables.get(relation.children[0].name),
                self.destination_model.variables.get(relation.parent.name)])

        elif relation.is_or():  # this is a 1 to n relatinship with multiple childs
            # add the first cnf child1 or child2 or ... or childN or no parent)

            # first elem of the constraint
            alt_cnf = [-1 * self.destination_model.variables.get(relation.parent.name)]
            for child in relation.children:
                alt_cnf.append(self.destination_model.variables.get(child.name))
            self.r_cnf.append(alt_cnf)

            for child in relation.children:
                self.r_cnf.append([
                    -1 * self.destination_model.variables.get(child.name),
                    self.destination_model.variables.get(relation.parent.name)])

        elif relation.is_alternative():  # this is a 1 to 1 relatinship with multiple childs
            # add the first cnf child1 or child2 or ... or childN or no parent)

            # first elem of the constraint
            alt_cnf = [-1 * self.destination_model.variables.get(relation.parent.name)]
            for child in relation.children:
                alt_cnf.append(self.destination_model.variables.get(child.name))
            self.r_cnf.append(alt_cnf)

            for i in range(len(relation.children)):
                for j in range(i + 1, len(relation.children)):
                    if i != j:
                        self.r_cnf.append([
                            -1 * self.destination_model.variables.get(relation.children[i].name),
                            -1 * self.destination_model.variables.get(relation.children[j].name)
                        ])
                self.r_cnf.append([
                    -1 * self.destination_model.variables.get(relation.children[i].name),
                    self.destination_model.variables.get(relation.parent.name)
                ])

        else:  # This is a m to n relationship
            print(
                "Fatal error. N to M relationships are not yet supported in PySAT",
                file=sys.stderr
            )
            raise NotImplementedError

    @staticmethod
    def and_combinator(cnfs_left: Any, cnfs_rigth: Any):
        '''
        Este metodo se encarga de la combinatoria de literales y clausulas concatenados por un
        operador and. Este operador trabaja por union de las variables.
        '''
        cnfs_left.extend(cnfs_rigth)
        return cnfs_left

    @staticmethod
    def or_combinator(cnfs_left: Any, cnfs_rigth: Any):
        '''
        Este metodo se encarga de la combinatoria de literales y clausulas concatenados por un 
        operador or. Este operador trabaja por combinancion de las variables.
        '''
        result = []
        for result1 in cnfs_left:
            for result2 in cnfs_rigth:
                cnf = copy.copy(result1)
                cnf.extend(result2)
                result.append(cnf)
        return result

    def get_var(self, ctc, node, name, number):
        childs = ctc.ast.get_childs(node)
        if name == 'not':
            var = self.destination_model.variables.get(
                ctc.ast.get_childs(node)[0].get_name()
            )
            if var:
                result =  [[-var * number]]
            else:
                cnfs = self.ast_iterator(ctc, childs[0], number * -1)
                result = cnfs
        else:
            var = self.destination_model.variables.get(node.get_name())
            result = [[var * number]]
        return result

    def ast_iterator(self, ctc, node, number: int):
        '''
        La variable number se utiliza para seguir las leyes de Morgan expuestas a continuación.
        Reglas de las leyes de Morgan:
            A <=> B      = (A => B) AND (B => A)
            A  => B      = NOT(A) OR  B
            NOT(A AND B) = NOT(A) OR  NOT(B) 
            NOT(A OR  B) = NOT(A) AND NOT(B) 
        '''
        name = node.get_name()
        childs = ctc.ast.get_childs(node)

        if name in ('and', 'or'):
            cnfs_left = self.ast_iterator(ctc, childs[0], number)
            cnfs_rigth = self.ast_iterator(ctc, childs[1], number)
        elif name in ('requires', 'implies'):
            cnfs_left = self.ast_iterator(ctc, childs[0], number * -1)
            cnfs_rigth = self.ast_iterator(ctc, childs[1], number)
        elif name == 'excludes':
            cnfs_left = self.ast_iterator(ctc, childs[0], number * -1)
            cnfs_rigth = self.ast_iterator(ctc, childs[1], number * -1)
        else:
            return self.get_var(ctc, node, name, number)

        if number > 0 and name == 'and':
            result = self.and_combinator(cnfs_left, cnfs_rigth)
        elif number > 0 and name in ('or', 'requires', 'excludes', 'implies'):
            result = self.or_combinator(cnfs_left, cnfs_rigth)
        elif number < 0 and name == 'and':
            result = self.or_combinator(cnfs_left, cnfs_rigth)
        elif number < 0 and name in ('or', 'requires', 'excludes', 'implies'):
            result = self.and_combinator(cnfs_left, cnfs_rigth)

        return result

    def add_constraint(self, ctc):
        node = ctc.ast.get_root()
        name = node.get_name()

        if (
            name in ('and', 'or', 'requires', 'excludes', 'implies', 'not')
            or self.destination_model.variables.get(name)
        ):
            cnfs = self.ast_iterator(ctc, node, 1)
        else:
            print('This FM contains non supported elements', file=sys.stderr)

        self.cnf.extend(cnfs)

    def transform(self):
        for feature in self.source_model.get_features():
            self.add_feature(feature)

        self.add_root(self.source_model.root)

        for relation in self.source_model.get_relations():
            self.add_relation(relation)

        for constraint in self.source_model.get_constraints():
            self.add_constraint(constraint)

        return self.destination_model
