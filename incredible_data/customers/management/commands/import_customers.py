import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("json_file", type=str)

    def handle(self, *args: Any, **options: Any) -> str | None:
        json_file_str: str = options["json_file"]
        json_file = Path(json_file_str)
        if not json_file.exists():
            msg = "Input file does not exist."
            raise CommandError(msg)

        with Path.open(json_file) as f:
            return json.loads(f.read())
