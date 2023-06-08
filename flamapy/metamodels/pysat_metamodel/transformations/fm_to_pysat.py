import itertools
from typing import Any

from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models.feature_model import (
    FeatureModel,
    Constraint,
    Feature,
    Relation,
)
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class FmToPysat(ModelToModel):
    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'pysat'

    def __init__(self, source_model: FeatureModel) -> None:
        self.source_model = source_model
        self.counter = 1
        self.destination_model = PySATModel()
        # self.r_cnf = self.destination_model.r_cnf
        # self.ctc_cnf = self.destination_model.ctc_cnf

    def add_feature(self, feature: Feature) -> None:
        if feature.name not in self.destination_model.variables:
            self.destination_model.variables[feature.name] = self.counter
            self.destination_model.features[self.counter] = feature.name
            self.counter += 1

    def add_root(self, feature: Feature) -> None:
        # self.r_cnf.append([self.destination_model.variables.get(feature.name)])
        value = self.destination_model.get_variable(feature.name)
        self.destination_model.add_clause([value])

    def add_relation(self, relation: Relation) -> None:  # noqa: MC0001
        value_parent = self.destination_model.get_variable(relation.parent.name)
        value_children = self.destination_model.get_variable(relation.children[0].name)

        if relation.is_mandatory():
            self.destination_model.add_clause([-1 * value_parent, value_children])
            self.destination_model.add_clause([-1 * value_children, value_parent])

        elif relation.is_optional():
            self.destination_model.add_clause([-1 * value_children, value_parent])

        elif relation.is_or():  # this is a 1 to n relatinship with multiple childs
            # add the first cnf child1 or child2 or ... or childN or no parent)
            # first elem of the constraint
            alt_cnf = [-1 * value_parent]
            for child in relation.children:
                alt_cnf.append(self.destination_model.get_variable(child.name))
            self.destination_model.add_clause(alt_cnf)

            for child in relation.children:
                self.destination_model.add_clause([
                    -1 * self.destination_model.get_variable(child.name),
                    value_parent
                ])

        # TODO: fix too many nested blocks
        elif relation.is_alternative():  # pylint: disable=too-many-nested-blocks
            # this is a 1 to 1 relatinship with multiple childs
            # add the first cnf child1 or child2 or ... or childN or no parent)

            # first elem of the constraint
            alt_cnf = [-1 * value_parent]
            for child in relation.children:
                alt_cnf.append(self.destination_model.get_variable(child.name))
            self.destination_model.add_clause(alt_cnf)

            for i, _ in enumerate(relation.children):
                for j in range(i + 1, len(relation.children)):
                    if i != j:
                        self.destination_model.add_clause([
                            -1 * self.destination_model.get_variable(relation.children[i].name),
                            -1 * self.destination_model.get_variable(relation.children[j].name)
                        ])
                self.destination_model.add_clause([
                    -1 * self.destination_model.get_variable(relation.children[i].name),
                    value_parent
                ])

        else:
            # This is a _min to _max relationship
            _min = relation.card_min
            _max = relation.card_max
            for val in range(len(relation.children) + 1):
                if val < _min or val > _max:
                    # combinations of val elements
                    for combination in itertools.combinations(relation.children, val):
                        cnf = [-1 * value_parent]
                        for feat in relation.children:
                            if feat in combination:
                                cnf.append(-1 * self.destination_model.get_variable(feat.name))
                            else:
                                cnf.append(self.destination_model.get_variable(feat.name))
                        self.destination_model.add_clause(cnf)

            # there is a special case when coping with the upper part of the thru table
            # In the case of allowing 0 childs, you cannot exclude the option  in that
            # no feature in this relation is activated
            for val in range(1, len(relation.children) + 1):

                for combination in itertools.combinations(relation.children, val):
                    cnf = [value_parent]
                    for feat in relation.children:
                        if feat in combination:
                            cnf.append(-1 * self.destination_model.get_variable(feat.name))
                        else:
                            cnf.append(self.destination_model.get_variable(feat.name))
                    self.destination_model.add_clause(cnf)

    def add_constraint(self, ctc: Constraint) -> None:
        def get_term_variable(term: Any) -> int:
            if term.startswith('-'):
                return -self.destination_model.get_variable(term[1:])

            return self.destination_model.get_variable(term)

        clauses = ctc.ast.get_clauses()
        for clause in clauses:
            clause_variables = list(map(get_term_variable, clause))
            self.destination_model.add_clause(clause_variables)

    def transform(self) -> PySATModel:
        for feature in self.source_model.get_features():
            self.add_feature(feature)

        self.add_root(self.source_model.root)

        for relation in self.source_model.get_relations():
            self.add_relation(relation)

        for constraint in self.source_model.get_constraints():
            self.add_constraint(constraint)

        return self.destination_model
