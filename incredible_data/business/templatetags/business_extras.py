import re

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.html import conditional_escape, format_html
from furl import furl
from loguru import logger
from moneyed import Money

register = template.Library()


@register.filter
def currency(value: float, currency: str = "USD"):
    """Format number as currency

    Currently only supports USD which is default"""
    match currency:
        case "USD":
            dollars = round(float(value), 2)
            return f"${intcomma(int(dollars))}{dollars:.2f}[-3:]"
        case _:
            return value


def bump_to_minimum(value: int, minimum: int) -> int:
    """Bump value up to minimum."""
    return minimum if value < minimum else value


@register.filter(needs_autoescape=True)
def usd_accounting(value: float | None, decimals: int = 2, *, autoescape=True):
    """Format number as accounting.

    For USD adds whitespace between $ and numbers to right align digits and left align $
    """
    if value is None:
        return None

    value_str = str(value)

    value_str = conditional_escape(value_str) if autoescape else value_str

    decimals = bump_to_minimum(decimals, 2)

    dollars = prepare_for_currency(value_str, decimals)

    formatted_dollars = f"{dollars:,.{decimals}f}"

    return format_html(
        (
            '<table style="width: 100%"><td align="left">$</td>'
            '<td align="right">{dollars}</td></table>'
        ),
        dollars=formatted_dollars,
    )


def attempt_float(value) -> bool:
    """Return whether <value> can convert to 'float' type."""
    try:
        float(value)
    except ValueError:
        return False

    return True


def prepare_for_currency(value: float | Money | str, decimals: int = 2) -> float:
    if isinstance(value, str):
        value_str = re.sub(r"[^0-9.]", "", value)
        value = float(value_str)

    if isinstance(value, Money):
        value = float(value.amount)

    return round(value, decimals)


@register.filter
def percent(value: float, decimal_places: int | None = None):
    """Return human-readable percent of input.

    E.g. '95.436'|numeric2percent becomes '95.436%'
         '95.436'|numeric2percent:2 becomes '95.44%'
         '95.4'|numeric2percent:2 becomes '95.4%'
    """
    if not decimal_places or value.is_integer():
        return_value = f"{value:g}%"
    else:
        value = round(value, decimal_places)
        return_value = f"{value:g}%"

    return return_value


@register.filter
def numeric2percent(value: float, decimal_places: int | None = None):
    """Return human-readable percent of decimal.

    E.g. '.086'|numeric2percent becomes '8.6%'
         '.086'|numeric2percent:2 becomes '8.6%'
    """
    as_percent = float(value * 100)
    if not decimal_places:
        return_value = f"{as_percent:g}%"
    else:
        as_percent = round(as_percent, decimal_places)
        return_value = f"{as_percent:g}%"

    return return_value


@register.filter
@stringfilter
def camel_case_split(value: str) -> str:
    """Split camel case word into multiple strings"""
    if not value:
        return ""
    split_strings = re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", value)

    new_string = ""
    for s in split_strings:
        new_string += s + " "

    return new_string[:-1]  # remove final space because of for loop


@register.filter(needs_autoescape=True)
@stringfilter
def urlizespecify(value: str, href: str, *, autoescape=True) -> str:
    """Similar to Django's `urlize` but allows for custom text."""
    if autoescape:
        value = conditional_escape(value)

    return f'<a href="{href}">{value}</a>'


@register.filter(needs_autoescape=True)
@stringfilter
def urlizespecifyblank(value: str, href: str, *, autoescape=True) -> str:
    """Similar to Django's `urlize` but allows for custom text."""
    if autoescape:
        value = conditional_escape(value)

    return (
        f'<a href="{href}" target="_blank" rel="noopener noreferrer">{value}'
        '<i class="fa-solid fa-up-right-from-square" data-fa-transform="shrink-6 up-4">'
        "</i></a>"
    )


@register.filter(needs_autoescape=True)
def urlizeobject(instance, *, autoescape=True):
    """Create a link for an object using it's `get_absolute_url` method, if it has one.

    :param object: The object/model to create a link for
    :type object: models.Model
    :return: If <object> has a `get_absolute_url` method, return a link tag in the form
        '<a href="{{ object.get_absolute_url }}">{{ object }}</a>';
        if no method exists, return {{ object }}.
    :rtype: str, marked safe
    """
    text = str(instance)
    try:
        url = instance.get_absolute_url()
    except Exception as e:  # noqa: BLE001
        # TODO: figure out what the correct exception is
        logger.exception(e)
        return text
    else:
        return f'<a href="{url}">{text}</a>'


@register.filter(needs_autoescape=True)
def urlizespecifyobject(value: str, instance, *, autoescape=True):
    """Create a link for an object using it's `get_absolute_url` method, if it has one.

    :param object: The object/model to create a link for
    :type object: models.Model
    :return: If <object> has a `get_absolute_url` method, return a link tag in the form
        '<a href="{{ object.get_absolute_url }}">{{ value }}</a>';
        if no method exists, return {{ object }}.
    :rtype: str, marked safe
    """
    text = str(value)
    try:
        url = instance.get_absolute_url()
    except Exception as e:  # noqa: BLE001
        # TODO: figure out what the correct exception is
        logger.exception(e)
        return text
    else:
        return f'<a href="{url}">{text}</a>'


@register.filter
@stringfilter
def replace(value: str, chars: str) -> str:
    """Replaces any of characters before vertical pipe '|' with character after pipe."""
    old_chars = chars.split("|")
    for i in old_chars[0]:
        value = value.replace(i, old_chars[1])
    return value


@register.simple_tag
def urlquery(path: str, param_name: str, param_val: str) -> str:
    """Include query in tag

    {% url "name" "param_name" param %}

    output: /reversed/path/?param_name=param"""
    path_reverse = reverse(path)
    fragment = furl(path_reverse)
    fragment.args[param_name] = param_val

    return fragment.url
