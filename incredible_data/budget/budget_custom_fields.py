import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .budget_custom_form_fields import (
    SimplePercentageField as SimplePercentageFormField,
)

logger = logging.getLogger(__name__)
log_kwargs = {
    "logger": logger,
}
if settings.DEBUG:
    logger.setLevel("DEBUG")

    log_kwargs.update(level=logging.DEBUG)
else:
    log_kwargs.update(level=logger.root.level)


class SimplePercentageField(models.DecimalField):
    """Enter and display percentages out of 100 but store them out of 1
    in db as decimals

    Because this is based on `models.DecimalField`, `decimal_places` applies to what is
    stored in the db (/1), not what is shown or typed in (/100). With that said, add two
    (2) to whatever is desired in the form for proper validation.
    """

    description = _(
        "percentage (max {max_digits} digits; {decimal_places} decimal places"
    )
    log_name = "models.PercentageField"

    def __init__(
        self,
        verbose_name=None,
        name=None,
        max_digits=None,
        decimal_places=None,
        **kwargs,
    ):
        if decimal_places is not None:
            self.humanize_decimal_places = int(decimal_places) - 2
        else:
            self.humanize_decimal_places = None

        kwargs.update(
            {
                "max_digits": max_digits,
                "decimal_places": decimal_places,
            }
        )

        super().__init__(verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        log_kwargs["path"] = f"{logger.name}.formfield"
        defaults = {"form_class": SimplePercentageFormField}
        kwargs.update(
            decimal_places=self.decimal_places - 2,
        )
        defaults.update(kwargs)

        return super().formfield(**defaults)
