import sys
from typing import Any

from famapy.core.exceptions import ElementNotFound
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

    def combinator(self, cnfs_left: Any, cnfs_rigth: Any, actual_op: str):
        '''
        Este metodo se encarga de conseguir las clausulas CNF resultantes por la combinacion de los
        resultados entre diferentes tipos de operados logicos.
        '''
        result = []
        if isinstance(cnfs_left, list) and isinstance(cnfs_rigth, list):
            if actual_op == 'and':
                for cnf_left in cnfs_left:
                    result.append(cnf_left)
                for cnf_rigth in cnfs_rigth:
                    result.append(cnf_rigth)
            elif actual_op in ('or', 'requires', 'implies', 'excludes'):
                for result1 in cnfs_left:
                    for result2 in cnfs_rigth:
                        cnf = [x for x in result1]
                        cnf.extend(result2)
                        result.append(cnf)
        elif isinstance(cnfs_left, int) and isinstance(cnfs_rigth, list):
            if actual_op == 'and':
                result.append([cnfs_left])
                for cnf_rigth in cnfs_rigth:
                    result.append(cnf_rigth)
            elif actual_op in ('or', 'requires', 'implies', 'excludes'):
                for cnf_rigth in cnfs_rigth:
                    cnf = [cnfs_left]
                    cnf.extend(cnf_rigth)
                    result.append(cnf)
        elif isinstance(cnfs_left, list) and isinstance(cnfs_rigth, int):
            if actual_op == 'and':
                result.append(cnfs_rigth)
                for cnf_left in cnfs_left:
                    result.append(cnf_left)
            elif actual_op in ('or', 'requires', 'implies', 'excludes'):
                for cnf_left in cnfs_left:
                    cnf = cnf_left
                    cnf.append(cnfs_rigth)
                    result.append(cnf)
        else: #left int and right int
            if actual_op == 'and':
                result.append([cnfs_left])
                result.append([cnfs_rigth])
            elif actual_op in ('or', 'requires', 'implies', 'excludes'):
                result = [[cnfs_left,cnfs_rigth]]
        return result

    def ast_iterator(self, ctc, node, number):
        '''
        La variable number se utiliza para seguir las leyes de morgan expuestas a continuación.
        Reglas de las leyes de Morgan:
            A <=> B      = (A => B) AND (B => A)
            A  => B      = NOT(A) OR  B
            NOT(A AND B) = NOT(A) OR  NOT(B) 
            NOT(A OR  B) = NOT(A) AND NOT(B) 
        '''
        result = []
        name = node.get_name()
        childs = ctc.ast.get_childs(node)
        if name == 'and':
            cnfs_left = self.ast_iterator(ctc, childs[0], number)
            cnfs_rigth = self.ast_iterator(ctc, childs[1], number)
            result = self.combinator(cnfs_left, cnfs_rigth, name if number > 0 else 'or')
        elif name == 'or':
            cnfs_left = self.ast_iterator(ctc, childs[0], number)
            cnfs_rigth = self.ast_iterator(ctc, childs[1], number)
            result = self.combinator(cnfs_left, cnfs_rigth, name if number > 0 else 'and')
        elif name in ('requires', 'implies'):
            cnfs_left = self.ast_iterator(ctc, childs[0], number * -1)
            cnfs_rigth = self.ast_iterator(ctc, childs[1], number)
            result = self.combinator(cnfs_left, cnfs_rigth, name)
        elif name == 'excludes':
            cnfs_left = self.ast_iterator(ctc, childs[0], number * -1)
            cnfs_rigth = self.ast_iterator(ctc, childs[1], number * -1)
            result = self.combinator(cnfs_left, cnfs_rigth, name)
        elif name == 'not':
            var = self.destination_model.variables.get(
                ctc.ast.get_childs(node)[0].get_name()
            )
            if var:
                result = -var * number
            else:
                cnfs = self.ast_iterator(ctc, childs[0], number * -1)
                result = cnfs
        else:
            var = self.destination_model.variables.get(node.get_name())
            result = var * number
        return result

    def add_constraint(self, ctc):
        node = ctc.ast.get_root()
        if node.get_name() in ('and', 'or', 'requires', 'excludes', 'implies', 'not'):
            cnfs = self.ast_iterator(ctc, node, 1)
        else:
            print('This FM contains non supported elements', file=sys.stderr)

        if isinstance(cnfs, list):
            for cnf in cnfs:
                if isinstance(cnf, list):
                    self.ctc_cnf.append(cnf)
                else:
                    self.ctc_cnf.append([cnf])
        else:
            self.ctc_cnf.append([cnfs])

    def transform(self):
        for feature in self.source_model.get_features():
            self.add_feature(feature)

        self.add_root(self.source_model.root)

        for relation in self.source_model.get_relations():
            self.add_relation(relation)

        for constraint in self.source_model.get_constraints():
            self.add_constraint(constraint)

        return self.destination_model
