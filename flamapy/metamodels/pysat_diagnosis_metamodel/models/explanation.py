"""Human-readable explanation values returned by the explain_* operations.

Each item names a relationship or cross-tree constraint of the model (the same
descriptions the diagnosis encoder records), and keeps the underlying assumption index so
tools can act on the result programmatically.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ExplanationItem:
    constraint_repr: str    # human-readable description of the relationship/constraint
    index: int              # assumption id in the diagnosis model (machine-usable)
    kind: str               # 'relationship' (tree) | 'constraint' (cross-tree)

    def __str__(self) -> str:
        return self.constraint_repr


@dataclass(frozen=True)
class Explanation:
    items: tuple[ExplanationItem, ...] = ()

    def descriptions(self) -> list[str]:
        return [item.constraint_repr for item in self.items]

    def __bool__(self) -> bool:
        return bool(self.items)

    def __str__(self) -> str:
        if not self.items:
            return 'No conflict found.'
        return '\n'.join(
            f'{number}. {item.constraint_repr}'
            for number, item in enumerate(self.items, start=1))
