from django.urls import path, register_converter
from django.views.generic.base import TemplateView

from incredible_data.mood import converters, views

register_converter(converters.EntryIdConverter, "entry")

app_name = "mood"
# fmt: off
urlpatterns = [
    path("", views.mood_entry_list, name="entry-list"),
    path("rating-widget/", views.rating_widget, name="rating_widget"),
    path("user-metric-chart/", TemplateView.as_view(template_name="mood/user_metric_chart.html"), name="user_metric_chart"),
    path("add/", views.mood_entry, name="entry-create"),
    path("<entry:entry>/", views.mood_entry_detail, name="entry-detail"),
    path("<entry:entry>/edit/", views.mood_entry_edit, name="entry-edit"),
]
# fmt: on
