from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.utils.translation import gettext_lazy as _

from incredible_data.bins.models.bins_container_models import Container


class Command(BaseCommand):
    help = _("Create multiple empty containers for label creation.")

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("count", nargs="+", type=int)

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write(self.style.NOTICE(f"'Count': {options['count']}"))
        for _idx in range(options["count"][0]):
            new_container = Container.objects.create(
                contents="!!!REPLACE ME!!!",
                style_id=1,
                created_by_id=1,
                modified_by_id=1,
            )

            self.stdout.write(
                self.style.SUCCESS(f"Created new container id '{new_container.id}'")
            )
