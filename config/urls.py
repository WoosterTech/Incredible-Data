# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from neapolitan.views import Role

from incredible_data.business.views import (
    InvoiceListView,
    InvoiceView,
    ProjectListView,
    ProjectView,
    printable_invoice,
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # path("grappelli/", include("grappelli.urls")),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("incredible_data.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    # path("business/", include("incredible_data.business.urls", namespace="business")),
    path("budget/", include("incredible_data.budget.budget_urls", namespace="budget")),
    path("bins/", include("incredible_data.bins.urls", namespace="bins")),
    path("qr_code/", include("qr_code.urls", namespace="qr_code")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

neapolitan_urlpatterns = [
    *ProjectView.get_urls(roles=[Role.CREATE, Role.DELETE, Role.DETAIL, Role.LIST]),
    # path("project/", ProjectListView.as_view(), name="project-list"),
    path("invoice/", InvoiceListView.as_view(), name="invoice-create"),
    *InvoiceView.get_urls(roles=[Role.CREATE, Role.UPDATE, Role.DETAIL, Role.DELETE]),
    path("invoice/<slug:slug>/printable/", printable_invoice, name="invoice-print"),
]

urlpatterns.extend(neapolitan_urlpatterns)
