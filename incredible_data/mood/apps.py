from typing import final

from django.apps import AppConfig


@final
class MoodConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incredible_data.mood"
