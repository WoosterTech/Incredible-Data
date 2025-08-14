from django.db import models

"""
JSONField automatically serializes most Python terms to JSON data.
Creates a TEXT field with a default value of "{}".  See test_json.py for
more information.

 from django.db import models
 from django_extensions.db.fields import json

 class LOL(models.Model):
     extra = json.JSONField()
"""

def dumps(value):  # -> str:
    ...
def loads(txt):  # -> Any:
    ...

class JSONDict(dict):
    def __repr__(self):  # -> str:
        ...

class JSONList(list):
    def __repr__(self):  # -> str:
        ...

class JSONField(models.TextField):
    def __init__(self, *args, **kwargs) -> None: ...
    def get_default(self):  # -> dict[Any, Any] | JSONDict | JSONList | Any:
        ...
    def to_python(self, value):  # -> dict[Any, Any] | JSONDict | JSONList | Any:
        ...
    def get_prep_value(self, value):  # -> str | Any:
        ...
    def from_db_value(
        self, value, expression, connection
    ):  # -> dict[Any, Any] | JSONDict | JSONList | Any:
        ...
    def get_db_prep_save(self, value, connection, **kwargs):  # -> str | None:
        ...
    def deconstruct(self):  # -> tuple[str, str, Sequence[Any], dict[str, Any]]:
        ...
