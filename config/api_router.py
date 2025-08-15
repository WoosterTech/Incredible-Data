from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from incredible_data.mood.api.views import MetricTypeViewSet
from incredible_data.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()  # pyright: ignore[reportAny]

router.register("users", UserViewSet)
router.register("mood", MetricTypeViewSet)


app_name = "api"
urlpatterns = router.urls
