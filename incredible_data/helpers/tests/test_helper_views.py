import pytest
from django.core.exceptions import PermissionDenied

from incredible_data.helpers.helper_views import UserStampedCreateView


class DummyRequest:
    def __init__(self, user):
        self.user = user


class DummyUser:
    def __init__(self, pk, authenticated=True):  # noqa: FBT002
        self.pk = pk
        self.is_authenticated = authenticated


class DummySuperView:
    def get_initial(self):
        return {}


class TestView(UserStampedCreateView, DummySuperView):
    def __init__(self, user):
        self.request = DummyRequest(user)

    def get_initial(self):
        return super().get_initial()


@pytest.mark.skip("this needs some work")
def test_get_initial_authenticated():
    user = DummyUser(pk=123, authenticated=True)
    view = TestView(user)
    initial = view.get_initial()
    assert initial["created_by"] == "123"
    assert initial["modified_by"] == "123"


@pytest.mark.skip("this needs some work")
def test_get_initial_unauthenticated():
    user = DummyUser(pk=123, authenticated=False)
    view = TestView(user)
    with pytest.raises(PermissionDenied):
        view.get_initial()
