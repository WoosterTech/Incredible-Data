import random
from collections.abc import Iterable, Sequence
from enum import Enum
from typing import Any, NamedTuple, cast

from attrmagic import ClassBase, SimpleDict, SimpleRoot
from constance import config
from pydantic import field_validator
from pydantic_extra_types.color import COLORS_BY_NAME, Color, ColorType

__all__ = ["COLOR_CHOICES"]


class ColorModel(ClassBase):
    name: str
    rgb: tuple[int, int, int]


class PaletteTuple(NamedTuple):
    hex: str
    name: str


class ColorChoices(SimpleRoot[Color]):
    @field_validator("root", mode="before")
    @classmethod
    def validate_root(cls, data: Any) -> Any:  # pyright: ignore[reportExplicitAny, reportAny]
        if not isinstance(data, dict):
            return data  # pyright: ignore[reportAny]
        if "root" in data:
            return data  # pyright: ignore[reportUnknownVariableType]

        return [Color(value) for value in data.values()]  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]

    def get_random_unique(self, existing_hex: set[str]) -> Color:
        available = [color for color in self if color.as_hex() not in existing_hex]
        if not available:
            msg = "No unique color found."
            raise ValueError(msg)
        return random.choice(available)  # noqa: S311

    def named_color_palette(self, names: Iterable[str], /):
        for name in names:
            color = next((c for c in self if c.as_named(fallback=True) == name), None)
            if color:
                yield PaletteTuple(hex=color.as_hex(), name=name)
            else:
                msg = f"No matching color found for name: {name}"
                raise ValueError(msg)

    def random_color_palette(self, count: int = 6) -> list[Color]:
        if count < 1:
            msg = "Count must be at least 1."
            raise ValueError(msg)
        return random.sample(self.root, min(count, len(self)))


COLOR_CHOICES = ColorChoices.model_validate(COLORS_BY_NAME)


def get_color_palette():
    names = cast("list[str]", config.MOOD_GRAPH_COLORS)
    return COLOR_CHOICES.named_color_palette(names)
