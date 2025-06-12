from typing import TYPE_CHECKING, ClassVar, final, override

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField as EmailField_
from django.urls import reverse  # pyright: ignore[reportUnknownVariableType]
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

if TYPE_CHECKING:
    from django.db.models.expressions import Combinable

    NameField = CharField[str | int | Combinable, str]
    EmailField = EmailField_[str | int | Combinable, str]
else:
    NameField = CharField
    EmailField = EmailField_


@final
class User(AbstractUser):
    """
    Default custom user model for Incredible Data.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = NameField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()  # pyright: ignore[reportIncompatibleVariableOverride]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.pk})  # pyright: ignore[reportAny]

    @override
    def __str__(self) -> str:
        if self.name.strip() == "":
            return self.email
        return self.name
