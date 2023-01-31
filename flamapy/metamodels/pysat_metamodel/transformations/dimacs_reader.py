from flamapy.core.transformations import TextToModel

from flamapy.metamodels.pysat_metamodel.models import PySATModel


class DimacsReader(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'cnf'

    def __init__(self, path: str) -> None:
        self.path = path

    def transform(self) -> PySATModel:
        with open(self.path, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            try:
                header = lines[0]
                header_list = header.split()
                n_features = int(header_list[2])
                features_lines = lines[1:n_features+1]
                clauses_lines = lines[n_features+1:]
            except Exception as e:
                print(f'Incorrect Dimacs format of {self.path}')
                e.with_traceback()
                return None

        features, variables = self._parse_features_variables(features_lines)
        sat_model = PySATModel()
        sat_model.features = features
        sat_model.variables = variables
        self._parse_clauses(sat_model, clauses_lines)
        return sat_model

    def _parse_features_variables(self, lines: list[str]) -> tuple[dict[int, str], dict[str, int]]:
        features: dict[int, str] = {}
        variables: dict[str, int] = {}
        for line in lines:
            line_list = line.split()
            var = int(line_list[1])
            feature = line_list[2]
            features[var] = feature
            variables[feature] = var
        return (features, variables)
        
    def _parse_clauses(self, sat_model: PySATModel, lines: list[str]) -> None:
        for line in lines:
            clause = line.split()
            sat_model.add_clause([int(c) for c in clause if c != '0'])