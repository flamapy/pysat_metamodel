"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/hs/HSDAG.java
"""

from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis import utils
from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.hsdag.labeler.labeler import IHSLabelable, LabelerType, \
    AbstractHSParameters
from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.hsdag.node import Node, NodeStatus
from flamapy.metamodels.pysat_diagnosis_metamodel.operations.diagnosis.utils import diff, contains


class HSDAG:
    """
    Implementation of the HS-dag algorithm.
    IHSLabeler algorithms could return labels (conflict or diagnosis) which are not minimal.
    """

    def __init__(self, labeler: IHSLabelable) -> None:
        self.labeler = labeler  # could be FastDiag or QuickXPlain

        self.max_number_diagnoses = -1  # maximum number of diagnoses to be found
        self.max_number_conflicts = -1  # maximum number of conflicts to be found
        self.max_depth = 0  # maximum depth of the HS-dag

        self.node_labels = []  # list of diagnoses or conflicts found
        self.path_labels = []  # list of diagnoses or conflicts found

        self.root = None  # root node of the HS-dag
        self.open_nodes = []  # list of open nodes
        self.label_nodes_map = {}  # Map of <label, list of nodes which have the label as its label>
        self.nodes_lookup = {}  # Map of <pathLabel, Node>

    def get_conflicts(self):
        """
        Returns the list of conflicts found.
        """
        if self.labeler.get_type() == LabelerType.CONFLICT:
            return self.node_labels
        else:
            return self.path_labels

    def get_diagnoses(self):
        """
        Returns the list of diagnoses found.
        """
        if self.labeler.get_type() == LabelerType.CONFLICT:
            return self.path_labels
        else:
            return self.node_labels

    def should_stop_construction(self) -> bool:
        condition1 = self.max_number_diagnoses != -1 and self.max_number_diagnoses <= len(self.get_diagnoses())
        condition2 = self.max_number_conflicts != -1 and self.max_number_conflicts <= len(self.get_conflicts())
        return condition1 or condition2

    def construct(self):
        """
        Constructs the HS-dag.
        """
        param = self.labeler.get_initial_parameters()

        has_root_label = self.create_root(param)

        if not self.should_stop_construction() and has_root_label:
            self.create_nodes()

    def create_root(self, param: AbstractHSParameters) -> bool:
        """
        Creates the root node of the HS-dag.
        """
        has_root_label = True

        if not self.has_root():
            labels = self.compute_label(self.labeler, param)

            if len(labels) == 0:
                has_root_label = False
            else:  # create root node
                label = self.select_label(labels)
                self.root = Node.create_root(label, param)

                self.open_nodes.append(self.root)

                self.add_node_labels(labels)  # to reuse labels
                self.add_item_to_label_nodes_map(label, self.root)

        return has_root_label

    def create_nodes(self):
        """
        Creates nodes of the HS-dag.
        """
        while self.has_nodes_to_expand():
            node = self.get_next_node()

            if not node.is_root():
                if self.skip_node(node):
                    continue

                self.label(node)

                if self.should_stop_construction():
                    break

            if node.status == NodeStatus.OPEN:
                self.expand(node)

    def label(self, node: Node):
        """
        Labels a node - identify new conflict or diagnosis.
        """
        # Reusing labels - H(node) ∩ S = {}, then label node by S
        labels = self.get_reusable_labels(node)

        # compute labels if there are none to reuse
        if len(labels) == 0:
            labels = self.compute_label_from_node(self.labeler, node)

            self.process_labels(labels)

        if len(labels) > 0:
            label = self.select_label(labels)

            node.label = label
            self.add_item_to_label_nodes_map(label, node)

        else:  # found a path label
            self.found_a_path_label_at_node(node)

    def expand(self, nodeToExpand: Node):
        """
        Creates children of a node.
        """
        for arcLabel in nodeToExpand.label:
            param_parent_node = nodeToExpand.parameters
            new_param = self.labeler.identify_new_node_parameters(param_parent_node, arcLabel)

            # rule 1.a - reuse node
            node = self.get_reusable_node(nodeToExpand.path_label, arcLabel)
            if node is not None:
                node.add_parent(nodeToExpand)
            else:  # rule 1.b - generate a new node
                node = Node(parent=nodeToExpand, arc_label=arcLabel, parameters=new_param)
                hashcode = sum(node.path_label)
                self.nodes_lookup[hashcode] = node

                if not self.can_prune(node):
                    self.open_nodes.append(node)

    def add_item_to_label_nodes_map(self, label, node):
        """
        Adds a node to the label_nodes_map.
        """
        hashcode = sum(label)
        if hashcode in self.label_nodes_map.keys():
            self.label_nodes_map[hashcode].append(node)
        else:
            self.label_nodes_map[hashcode] = node

    @staticmethod
    def compute_label(labeler: IHSLabelable, param: AbstractHSParameters):
        return labeler.get_label(param)

    @staticmethod
    def compute_label_from_node(labeler: IHSLabelable, node: Node):
        param = node.parameters
        return HSDAG.compute_label(labeler, param)

    def add_node_labels(self, labels: list[list[int]]):
        for label in labels:
            self.node_labels.append(label)

    def found_a_path_label_at_node(self, node: Node):
        node.status = NodeStatus.CHECKED
        pathLabel = node.path_label.copy()

        self.path_labels.append(pathLabel)

    @staticmethod
    def select_label(labels):
        return labels[0]

    def has_nodes_to_expand(self):
        return len(self.open_nodes) > 0

    def get_next_node(self):
        return self.open_nodes.pop(0)

    def has_root(self):
        return self.root is not None

    # Pruning engine
    def skip_node(self, node: Node):
        condition1 = self.max_depth != 0 and self.max_depth < node.level
        return node.status != NodeStatus.OPEN or condition1 or self.can_prune(node)

    def can_prune(self, node: Node):
        # 3.i - if n is checked, and n'' is such that H(n) ⊆ H(n'), then close the node n''
        # n is a diagnosis
        for path_label in self.path_labels:
            # if node.path_label.containsAll(path_label):
            if all(elem in path_label for elem in node.path_label):
                node.status = NodeStatus.CLOSED
                return True

        # 3.ii - if n has been generated and node n'' is such that H(n') = H(n), then close node n''
        for n in self.open_nodes:
            if len(n.path_label) == len(node.path_label) \
                    and len(diff(n.path_label, node.path_label)) == 0:
                node.status = NodeStatus.CLOSED
                return True
        return False

    def get_reusable_labels(self, node: Node):
        labels = []
        for label in self.node_labels:
            # H(node) ∩ S = {}
            if not utils.hasIntersection(node.path_label, label):
                labels.append(label)
        return labels

    def get_reusable_node(self, path_labels, arc_label):
        if path_labels is None:
            h = [arc_label]
        else:
            h = path_labels.copy()
            h.append(arc_label)
        hashcode = sum(h)
        return self.nodes_lookup.get(hashcode)

    def process_labels(self, labels):
        if len(labels) > 0:
            # check existing and obtained labels for subset-relations
            non_min_labels = []

            for fs in self.node_labels:
                if contains(non_min_labels, fs):
                    continue

                for cs in labels:
                    if contains(non_min_labels, cs):
                        continue

                    greater = fs if len(fs) > len(cs) else cs
                    smaller = cs if len(fs) > len(cs) else fs

                    if utils.contains_all(greater, smaller):
                        non_min_labels.append(greater)

                        if len(greater) > len(smaller):
                            # update the DAG
                            nodes = self.label_nodes_map.get(greater)

                            if nodes is not None:
                                for nd in nodes:
                                    if nd.get_status() == NodeStatus.OPEN:
                                        nd.set_label(smaller)  # relabel the node with smaller
                                        self.add_item_to_label_nodes_map(smaller, nd)  # add new label to the map

                                        delete = diff(greater, smaller)
                                        for label in delete:
                                            child = nd.get_children().get(label)

                                            if child is not None:
                                                child.parents.remove(nd)
                                                nd.get_children().remove(label)
                                                self.clean_up_nodes(child)

            # remove the known non - minimal conflicts
            for label in non_min_labels:
                labels.remove(label)  # labels.removeAll(non_min_labels)
                del self.label_nodes_map[label]  # non_min_labels.forEach(label_nodesMap::remove)

            # add new labels to the list of labels
            self.add_node_labels(labels)
            # hsdag.addNodeLabels(labels)

    def clean_up_nodes(self, node: Node):
        del self.nodes_lookup[node.path_label]

        if node.status == NodeStatus.OPEN:
            node.status = NodeStatus.PRUNED

        # downward clean up
        for arcLabel in node.children.keys():
            child = node.children.get(arcLabel)
            if child is not None:
                self.clean_up_nodes(child)
