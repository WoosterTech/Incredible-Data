# pyright: reportAny=false
import http
from typing import TYPE_CHECKING, cast, override

from django import forms
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from incredible_data.helpers.helper_views import UserStampedCreateView
from incredible_data.users.models import User

if TYPE_CHECKING:
    from django.template.response import TemplateResponse


class DummyUserStampedCreateView(UserStampedCreateView):
    pass


class UserTestCase(TestCase):
    @override
    def setUp(self):
        self.user: User = User.objects.create_user(  # pyright: ignore[reportUnknownMemberType, reportUninitializedInstanceVariable]
            email="testuser@example.com",
            password="testpassword",  # noqa: S106
        )
        self.user.user_permissions.add(*Permission.objects.all())
        self.client: Client = Client()

    def test_user_created(self):
        user = User.objects.get(email="testuser@example.com")
        self.client.force_login(user)
        container_add_url = reverse("bins:container_add")
        response = cast("TemplateResponse", self.client.get(container_add_url))

        assert response.status_code == http.HTTPStatus.OK

        context_data = response.context_data

        assert context_data is not None

        form = context_data["form"]

        assert isinstance(form, forms.ModelForm)

        initial = form.initial

        assert "created_by" in initial

        created_by = initial["created_by"]

        assert created_by == str(user.pk)
