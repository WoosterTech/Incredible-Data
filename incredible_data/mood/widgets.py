from typing import TYPE_CHECKING, override

from django import forms
from django.template.loader import render_to_string
from django.urls import reverse  # pyright: ignore[reportUnknownVariableType]
from django.utils.safestring import SafeString, mark_safe

if TYPE_CHECKING:
    from django.forms.widgets import _OptAttrs  # pyright: ignore[reportPrivateUsage]


class EmojiDisplayWidget(forms.Widget):
    """
    A custom widget to display emojis in a form field.
    """

    template_name: str = "mood/rating_widget.html"
    max_rating: int = 5
    emoji: str = "⭐"

    def __init__(
        self, max_rating: int = 5, emoji: str = "⭐", attrs: "_OptAttrs | None" = None
    ) -> None:
        self.max_rating = max_rating
        self.emoji = emoji

        super().__init__(attrs)

    @override
    def render(
        self,
        name: str,
        value: int = 0,
        attrs=None,  # pyright: ignore[reportMissingParameterType]
        renderer=None,  # pyright: ignore[reportMissingParameterType]
    ) -> SafeString:
        ratings = list(range(1, self.max_rating + 1))

        html_context = {
            "hx_get_url": reverse("mood:rating_widget"),
            "name": name,
            "value": value,
            "ratings": ratings,
            "emoji": self.emoji,
        }

        widget_html = render_to_string(self.template_name, html_context)

        return mark_safe(  # noqa: S308
            f'<div id="{name}-stars" class="star-rating">{widget_html}</div>'
            f'<input type="hidden" name="{name}" value="{value}" id="id_{name}">'  # pyright: ignore[reportImplicitStringConcatenation]
        )
