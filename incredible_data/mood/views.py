from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse  # pyright: ignore[reportUnknownVariableType]
from django.utils.safestring import mark_safe

# Create your views here.


def rating_widget(request: HttpRequest) -> HttpResponse:
    query_dict = request.GET

    name = query_dict.get("name")
    value = int(query_dict.get("value", 0))
    max_rating = int(query_dict.get("max_rating", 5))
    emoji = query_dict.get("emoji", "⭐")

    ratings = list(range(1, max_rating + 1))

    html_context = {
        "hx_get_url": reverse("mood:rating_widget"),
        "name": name,
        "value": value,
        "ratings": ratings,
        "emoji": emoji,
    }

    widget_html = render_to_string("mood/rating_widget.html", html_context)

    script = f"<script>document.getElementById('id_{name}').value = {value};</script>"

    return HttpResponse(
        mark_safe(  # noqa: S308
            f'<div id="{name}-stars" class="star-rating">{widget_html}</div>{script}'
        )
    )
