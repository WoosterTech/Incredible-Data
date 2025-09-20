from django.urls import path
from django.views.generic.base import TemplateView

from incredible_data.mood import views

app_name = "mood"
# fmt: off
urlpatterns = [
    path("rating-widget/", views.rating_widget, name="rating_widget"),
    path("user-metric-chart/", TemplateView.as_view(template_name="mood/user_metric_chart.html"), name="user_metric_chart"),
    path("add/", views.entry_create_redirect, name="entry_create_redirect"),
]
# fmt: on
