# pyright: reportIncompatibleVariableOverride=warning


import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any, override

from django import forms
from django.core import checks, validators
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.db.models.expressions import Combinable
    from django.utils.functional import _Getter  # pyright: ignore[reportPrivateUsage]

    PositiveSmallIntegerField = models.PositiveSmallIntegerField[
        float | int | str | Combinable, int
    ]
else:
    PositiveSmallIntegerField = models.PositiveSmallIntegerField

logger = logging.getLogger(__name__)


class RatingField(PositiveSmallIntegerField):
    # a Promise is used here in Django fields
    description: "str | _Getter[str]" = _(  # pyright: ignore[reportAssignmentType]
        "A field for storing ratings on a user-specified scale."
    )
    allow_zero: bool = False
    scale_maximum: int = 10

    @override
    def check(self, **kwargs: Any) -> list[checks.CheckMessage]:  # pyright: ignore[reportAny, reportExplicitAny]
        errors = super().check(**kwargs)
        errors.extend(self._check_maximum_is_positive())
        return errors

    def _check_maximum_is_positive(self) -> list[checks.CheckMessage]:
        valid = True
        msg_postfix = None
        if self.allow_zero:
            if self.scale_maximum <= 0:
                valid = False
                msg_postfix = "zero"
        elif self.scale_maximum <= 1:
            valid = False
            msg_postfix = "one"
        if not valid:
            return [
                checks.Error(
                    f"'scale_maximum' must be greater than {msg_postfix}.",
                    obj=self,
                    id="incredible_data.E001",
                )
            ]
        return []

    def __init__(
        self,
        allow_zero: bool = False,  # noqa: FBT001, FBT002
        scale_maximum: int = 10,
        **kwargs: Any,  # pyright: ignore[reportExplicitAny, reportAny]
    ) -> None:
        super().__init__(**kwargs)  # pyright: ignore[reportAny]

        self.allow_zero = allow_zero
        self.scale_maximum = scale_maximum

    @cached_property
    def validators(self) -> list[validators.BaseValidator]:
        validators_ = super().validators

        msg = f"PostiveSmallIntegerField validators: {validators_}"
        logger.debug(msg)

        if not self.allow_zero:
            validators_.append(
                validators.MinValueValidator(
                    1, message=_("Rating cannot be less than %(limit_value)s.")
                )
            )
        validators_.append(
            validators.MaxValueValidator(
                self.scale_maximum,
                message=_("Rating cannot be greater than %(limit_value)s."),
            )
        )

        return validators_  # pyright: ignore[reportReturnType]  # super call has weird type?

    @override
    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.Field] | None = None,
        **kwargs: Any,  # pyright: ignore[reportAny, reportExplicitAny]
    ) -> forms.Field:
        kwargs["form_class"] = form_class
        kwargs["choices_form_class"] = choices_form_class

        start_value = 1 if not self.allow_zero else 0
        choices_tuple = tuple(
            (i, str(i)) for i in range(start_value, self.scale_maximum + 1)
        )
        kwargs.setdefault("choices", choices_tuple)
        kwargs.setdefault("min_value", start_value)
        kwargs.setdefault("max_value", self.scale_maximum)

        return super().formfield(**{"form_class": forms.ChoiceField, **kwargs})
