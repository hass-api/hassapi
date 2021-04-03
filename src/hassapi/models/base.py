"""Base Model classes."""

from dataclasses import asdict
from typing import Dict, List


class Model:
    """Base Model with repr() method."""

    def __repr__(self) -> str:
        """Get object repr()."""
        name = type(self).__name__
        return f"{name} with fields:\n" f"{_repr_dict(asdict(self))}"


class ModelList(List):
    """Base List of Model with repr() method."""

    def __repr__(self) -> str:
        """Get object repr()."""
        name = type(self).__name__
        items = [f"{name} with items: ["]

        for model in self:
            item = repr(model)
            items.append(f"- {item}\n\n")

        return "\n".join(items + ["]"])


def _repr_dict(d: Dict, indent: int = 4) -> str:
    """Get dictionary string representation."""
    lines = []
    tab = " " * indent

    for key, value in d.items():
        name = f"{tab}{key}: "
        if isinstance(value, dict):
            lines.append(name)
            lines.append(_repr_dict(value, indent * 2))
        else:
            lines.append(f"{name}{value}")

    return "\n".join(lines)
