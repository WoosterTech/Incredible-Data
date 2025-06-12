from django.urls import path

from incredible_data.mood import views

app_name = "mood"
# fmt: off
urlpatterns = [
    path("rating-widget/", views.rating_widget, name="rating_widget"),
]
# fmt: on
