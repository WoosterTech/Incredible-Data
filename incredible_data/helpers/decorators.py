from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, ParamSpec, TypeVar

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

_P = ParamSpec("_P")
_R = TypeVar("_R", bound="HttpResponse")


def create_view(func: Callable[_P, _R]):
    @wraps(func)
    def wrapper(request: "HttpRequest") -> _R:
        initial = request.GET.copy().dict()

        return func(request, initial=initial)  # pyright: ignore[reportUnknownVariableType, reportCallIssue]

    return wrapper
