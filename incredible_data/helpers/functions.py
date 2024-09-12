import logging
from pathlib import Path

from django.db.models.fields.files import FieldFile
from shortuuid import ShortUUID

logger = logging.getLogger(__name__)
logger.disabled = True


def truncate_string(s: str, *, max_length: int = 50, ellipses: str = "...") -> str:
    """Truncate a string to a certain length, preserving whole words.

    Examples:
        >>> truncate_string(
            "This is a long string that needs to be truncated to fit within a certain length.",
            max_length=21
        )
        'This is a long...'
        >>> truncate_string(
            "This is a long string that needs to be truncated to fit within a certain length.",
            max_length=25
        )
        'This is a long string...'

    Args:
        s: The string to truncate.
        max_length: The maximum length of the string. Defaults to 50.
        ellipses: The ellipses to add to the end of the truncated string. Defaults
            to "..."."

    Returns:
        The truncated string.
    """  # noqa: E501
    if len(s) <= max_length:
        return s

    ellipses_length = len(ellipses)
    truncated = s[: max_length - ellipses_length]
    last_space_index = truncated.rfind(" ")
    if last_space_index != -1:
        truncated = truncated[:last_space_index].strip()
    return truncated + ellipses


def short_uuid(
    *,
    alphabet: str = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
):
    """Generate a short UUID.

    The generated UUID is 5 characters long.

    Examples:
        >>> short_uuid()
        '4XJ3D'
        >>> short_uuid(alphabet="01345678")
        `74456`

    Args:
        alphabet: The alphabet to use for the UUID. Defaults
            to "23456789ABCDEFGHJKLMNPQRSTUVWXYZ".

    Returns:
        The short UUID.
    """
    su = ShortUUID(alphabet=alphabet)
    return su.uuid()[:5]


def create_media_name(field_file: FieldFile) -> str:
    """Get only the filename (`stem`) from a FieldFile."""
    if field_file.name is None:
        logger.warning("FieldFile has no name.")
        return ""
    return Path(field_file.name).stem
