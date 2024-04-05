import logging

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .incredible_data_helpers import Percent, is_number, plog

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel("DEBUG")

    log_kwargs = {
        "logger": logger,
        "level": logging.DEBUG,
    }
else:
    log_kwargs = {
        "logger": logger,
        "level": logging.root.level,
    }


class SimplePercentageField(forms.DecimalField):
    def __init__(
        self,
        *,
        max_value=None,
        min_value=None,
        max_digits=None,
        decimal_places=None,
        **kwargs,
    ):
        log_kwargs["path"] = f"{logger.name}.SimplePercentageField"
        if "widget" not in kwargs:
            step = 10 ** (-1 * decimal_places)
            kwargs["widget"] = forms.NumberInput(
                attrs={"class": "percent", "step": step}
            )
        self.max_digits, self.decimal_places = max_digits, decimal_places
        super().__init__(max_value=max_value, min_value=min_value, **kwargs)

    def to_python(self, value):
        log_kwargs["path"] = f"{logger.name}.to_python"
        plog(text="value", value=value, **log_kwargs)

        val = super().to_python(value)

        val_type = type(val) if settings.DEBUG else None
        plog(text=f"after super() val [{val_type}]", value=val, **log_kwargs)

        if isinstance(val, Percent):
            return val.value

        if is_number(val):
            new_val = Percent.fromform(val)

            rvalue = new_val.value

            rtype = type(rvalue) if settings.DEBUG else None
            plog(text=f"is_number return val [{rtype}]", value=rvalue, **log_kwargs)

            return rvalue

        rtype = type(val)
        raise ValidationError(
            _("Invalid value type: %(rtype)s"),
            code="invalid",
            params={"rtype": rtype},
        )

    def prepare_value(self, value):
        log_kwargs["path"] = f"{logger.name}.prepare_value"

        val = super().prepare_value(value)

        if isinstance(val, Percent):
            return val.per_hundred
        if is_number(val):
            if isinstance(val, str):
                new_val = Percent.fromform(val)

                return_value = new_val.per_hundred
                rtype = type(return_value) if settings.DEBUG else None

                plog(text=f"return value [{rtype}]", value=return_value, **log_kwargs)

                return return_value

            rvalue = Percent(val).per_hundred

            rtype = type(rvalue) if settings.DEBUG else None
            plog(text=f"return value [{rtype}]", value=rvalue, **log_kwargs)

            return rvalue

        return val
