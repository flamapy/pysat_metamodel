from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.operations import Operation
from flamapy.core.operations.descriptor import OperationDescriptor
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATBackbone(Operation):
    facade = OperationDescriptor(
        doc=(
            'Returns the backbone of the feature model: the set of features that must\n'
            'always be selected (core) and those that must never be selected (dead) across\n'
            "all valid configurations, grouped under 'core' and 'dead' keys."
        ),
        returns='Union[None, Dict[str, List[Any]]]',
        name='backbone', operation='PySATBackbone', default_backend='sat'
    )

    def __init__(self) -> None:
        self._result: dict[str, list[Any]] = {"core": [], "dead": []}


    def get_backbone(self) -> dict[str, list[Any]]:
        return self.get_result()

    def get_result(self) -> dict[str, list[Any]]:
        return self._result

    def execute(self, model: VariabilityModel) -> 'PySATBackbone':
        sat_model = cast(PySATModel, model)
        self._result = get_backbone(sat_model)
        return self


def get_backbone(model: PySATModel) -> dict[str, list[Any]]:
    # B <- Ø
    backbone_core = []
    backbone_dead = []

    id_to_name = model.features
    relevant_ids = set(id_to_name.keys())

    solver = Solver(name='glucose3')
    for clause in model.get_all_clauses().clauses:
        solver.add_clause(clause)

    # (out, C) <- SAT(phi)
    if not solver.solve():
        solver.delete()
        return {"core": [], "dead": list(id_to_name.values())}

    # 3. C <- filter(C)
    initial_model = solver.get_model()
    candidates = {lit for lit in initial_model if abs(lit) in relevant_ids}

    # while C != Ø do
    while candidates:
        # l <- pick a literal from C
        literal = next(iter(candidates))

        # (out, S) <- SAT(phi U {not l})
        if not solver.solve(assumptions=[-literal]):
            # out = unsat -> l is in the backbone
            name = id_to_name[abs(literal)]
            if literal > 0:
                backbone_core.append(name)
            else:
                backbone_dead.append(name)

            # C <- C \ {l}
            candidates.remove(literal)

            # phi <- phi U {l}
            solver.add_clause([literal])
        else:
            new_model_set = set(solver.get_model())
            # C <- C ∩ S
            candidates &= new_model_set
    solver.delete()
    return {"core": backbone_core, "dead": backbone_dead}
