import logging
from pathlib import Path
from typing import Protocol

from shortuuid import uuid

logger = logging.getLogger(__name__)
logger.disabled = True


def truncate_string(s: str, max_length: int = 50) -> str:
    """Truncate a string to a certain length, preserving whole words."""
    if len(s) <= max_length:
        return s
    truncated = s[: max_length - 3]
    last_space_index = truncated.rfind(" ")
    if last_space_index != -1:
        truncated = truncated[:last_space_index].strip()
    return truncated + "..."


def short_uuid(
    alphabet: str = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
):
    return str(uuid(alphabet=alphabet))[:5]


class FieldFileProtocol(Protocol):
    name: str


def create_media_name(field_file: FieldFileProtocol) -> str:
    """Get only the filename (`stem`) from a FieldFile."""
    return Path(field_file.name).stem
