# pyright: reportAny=false
from .filters import *  # noqa: F403

__version__: str = "25.1"

def parse_version(version: str) -> tuple[int | str, ...]: ...

VERSION: tuple[int | str, ...] = ...
