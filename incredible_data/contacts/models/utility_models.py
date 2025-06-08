# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportIncompatibleVariableOverride=false
from typing import final, override

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from pydantic import BaseModel


@final
class DocumentNumber(models.Model):
    document = models.CharField(max_length=50, primary_key=True, unique=True)
    prefix = models.CharField(max_length=10, blank=True)
    padding_digits = models.IntegerField(default=0)
    next_counter = models.IntegerField(default=1)
    last_number = models.CharField(max_length=50, editable=False)
    last_generated_date = models.DateTimeField(auto_now=True)

    @override
    def __str__(self) -> str:
        return f"Document({self.document}) | Last: {self.last_number}"

    def get_next_number(self):
        prefix = self.prefix
        next_counter = self.next_counter
        padded_counter = str(next_counter).zfill(self.padding_digits)  # pyright: ignore[reportUnknownArgumentType]
        number = f"{prefix}{padded_counter}"

        self.next_counter += 1
        self.last_number = number

        self.save()

        return number


class NumberConfig(BaseModel):
    prefix: str = ""
    width: int = 0
    start_value: int = 1


class NumberedModel(models.Model):
    """Creates a number field generated from the autofield `ID`.

    `ID` needs to be an int if modified from default.

    `f"{number_prefix}{str(self.id).zfill(number_width)}`

    Attributes:
        number_config: a NumberConfig instance with the following attributes:
            - prefix: str = ""
            - width: int = 0
            - start_value: int = 1


    Example:
        Assuming `number_prefix = "INV"` and `number_width = 4`, `INV0001`,
        `INV0002`, etc.
    """

    number = models.CharField(_("number"), unique=True, max_length=10, editable=False)  # pyright: ignore[reportUnannotatedClassAttribute]
    number_config: NumberConfig = NumberConfig()

    class Meta:
        abstract = True  # pyright: ignore[reportUnannotatedClassAttribute]

    @override
    def save(self, *args, **kwargs) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        if self._state.adding:
            config = self.number_config
            project_number, _ = DocumentNumber.objects.get_or_create(
                document=self.__class__.__name__,
                defaults={
                    "prefix": config.prefix,
                    "padding_digits": config.width,
                    "next_counter": config.start_value,
                },
            )
            self.number = project_number.get_next_number()
        return super().save(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]


class UserStampedModel(models.Model):
    created_by = models.ForeignKey(  # pyright: ignore[reportUnannotatedClassAttribute]
        settings.AUTH_USER_MODEL,  # pyright: ignore[reportAny]
        verbose_name=_("created by"),
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
    )
    modified_by = models.ForeignKey(  # pyright: ignore[reportUnannotatedClassAttribute]
        settings.AUTH_USER_MODEL,  # pyright: ignore[reportAny]
        verbose_name=_("modified by"),
        on_delete=models.CASCADE,
        related_name="%(class)s_modified_by",
    )

    class Meta:
        abstract = True  # pyright: ignore[reportUnannotatedClassAttribute]


class BaseNumberedModel(TimeStampedModel, UserStampedModel, NumberedModel):
    """Base class for Numbered models that include time and user stamps."""

    class Meta:
        abstract = True  # pyright: ignore[reportUnannotatedClassAttribute]
