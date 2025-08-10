# pyright: reportIncompatibleVariableOverride=warning


import logging
from functools import cached_property
from typing import Any, final, override

from django import forms
from django.core import checks, validators
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@final
class RatingField(models.PositiveSmallIntegerField):  # pyright: ignore[reportMissingTypeArgument]
    # a Promise is used here in Django fields
    description = _("A field for storing ratings on a user-specified scale.")
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
        super().__init__(**kwargs)

        self.allow_zero = allow_zero
        self.scale_maximum = scale_maximum

    @override
    def get_internal_type(self) -> str:
        return "PositiveSmallIntegerField"

    @cached_property
    @override
    def validators(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        validators_ = super().validators

        msg = f"IntegerField validators: {validators_}"
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

        return validators_

    @override
    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.Field] | None = None,
        **kwargs: Any,  # pyright: ignore[reportAny, reportExplicitAny]
    ) -> forms.Field:
        kwargs["form_class"] = forms.ChoiceField
        kwargs["choices_form_class"] = None

        start_value = 1 if not self.allow_zero else 0
        choices_tuple = tuple(
            (i, str(i)) for i in range(start_value, self.scale_maximum + 1)
        )
        kwargs["choices"] = choices_tuple
        kwargs["widget"] = forms.Select

        return super().formfield(**kwargs)  # pyright: ignore[reportAny]
