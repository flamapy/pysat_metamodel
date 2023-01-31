from flamapy.core.transformations import ModelToText

from flamapy.metamodels.pysat_metamodel.models import PySATModel


class DimacsWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'cnf'

    def __init__(self, path: str, source_model: PySATModel) -> None:
        self.path = path
        self.source_model = source_model

    def transform(self) -> str:
        dimacs_str = pysat_to_dimacs(self.source_model)
        with open(self.path, 'w', encoding='utf8') as file:
            file.write(dimacs_str)
        return dimacs_str


def pysat_to_dimacs(model: PySATModel) -> str:
    lines = []
    # Header
    features_dict = model.features
    clauses_list = model.get_all_clauses().clauses
    lines.append(f'p cnf {len(features_dict)} {len(clauses_list)}')
    for id, name in features_dict.items():
        lines.append(f'c {id} {name}')
    for clause in clauses_list:
        lines.append(f'{" ".join((str(c) for c in clause))}')
    return '\n'.join(lines)