import logging

from django.conf import settings
from django.urls import URLPattern, URLResolver, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from incredible_data.mood.api.views import (
    ChartAPIView,
    EntryViewSet,
    MetricTypeViewSet,
    MetricViewSet,
)
from incredible_data.users.api.views import UserViewSet

logger = logging.getLogger(__name__)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()  # pyright: ignore[reportAny]

router.register("users", UserViewSet)
router.register("mood/metric-types", MetricTypeViewSet)
router.register("mood/metrics", MetricViewSet)
router.register("mood/entries", EntryViewSet)

app_name = "api"
urlpatterns: list[URLPattern | URLResolver] = router.urls  # pyright: ignore[reportAny]

urlpatterns += [
    path("mood/chart/", ChartAPIView.as_view(), name="mood-chart"),
]
