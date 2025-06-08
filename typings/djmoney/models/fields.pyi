# pyright: reportPrivateUsage=false

from collections.abc import Iterable
from decimal import Decimal
from typing import TypeAlias

from django.db import models
from django.utils.functional import _Getter, _StrOrPromise
from djmoney.money import Money

_MoneyTypeAlias: TypeAlias = str | bytes | float | Decimal | Money

class MoneyField(models.DecimalField[_MoneyTypeAlias, Money]):
    description: str | _Getter[str]

    currency_max_length: int
    default_currency: str | None
    currency_choices: Iterable[tuple[str, str]]
    currency_field_name: str | None
    money_descriptor_class: type

    def __init__(
        self,
        verbose_name: _StrOrPromise | None = None,
        name: str | None = None,
        max_digits: int | None = None,
        decimal_places: int = ...,
        default: models.NOT_PROVIDED | _MoneyTypeAlias = ...,
        default_currency: str | None = ...,
        currency_choices: Iterable[tuple[str, str]] = ...,
        currency_max_length: int = ...,
        currency_field_name: str | None = None,
        money_descriptor_class: type = ...,
        **kwargs: object,
    ) -> None: ...
