from typing import TYPE_CHECKING, final, override

from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel

from incredible_data.contacts.models.utility_models import UserStampedModel

# Create your models here.
if TYPE_CHECKING:
    from django.db.models.expressions import Combinable

    from incredible_data.contacts.models.contacts_models import PhoneNumber

    CharField = models.CharField[str | int | Combinable, str]
    ForeignPhoneNumberField = models.ForeignKey[PhoneNumber | Combinable, PhoneNumber]
    ContactsM2MField = models.ManyToManyField[PhoneNumber, models.Model]
else:
    CharField = models.CharField
    ForeignPhoneNumberField = models.ForeignKey
    ContactsM2MField = models.ManyToManyField


@final
class Customer(TimeStampedModel, UserStampedModel):  # pyright: ignore[reportIncompatibleVariableOverride]
    name = CharField(_("customer"), max_length=100)
    main_phone = ForeignPhoneNumberField(
        "contacts.PhoneNumber",
        verbose_name=_("organization phone"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    contacts = ContactsM2MField(
        "contacts.Contact", verbose_name=_("contacts"), through="CustomerContact"
    )
    slug = AutoSlugField(populate_from="name")

    @override
    def __str__(self) -> str:
        return self.name

    @property
    def primary_contact(self) -> "CustomerContact | None":
        """
        Returns the primary contact for this customer, if it exists.
        """

        try:
            return self.customercontact_set.get(primary=True).contact
        except CustomerContact.DoesNotExist:
            return None


if TYPE_CHECKING:
    from incredible_data.contacts.models.contacts_models import Contact

    ForeignCustomerField = models.ForeignKey[Customer | Combinable, Customer]
    ForeignContactField = models.ForeignKey[Contact | Combinable, Contact]
    BooleanField = models.BooleanField[bool | Combinable, bool]
else:
    ForeignCustomerField = models.ForeignKey
    ForeignContactField = models.ForeignKey
    BooleanField = models.BooleanField


@final
class CustomerContact(models.Model):
    customer = ForeignCustomerField(
        Customer, verbose_name=_("customer"), on_delete=models.CASCADE
    )
    contact = ForeignContactField(
        "contacts.Contact", verbose_name=_("contact"), on_delete=models.CASCADE
    )
    primary = BooleanField(_("primary"), default=False)

    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        constraints = [
            UniqueConstraint(
                fields=["customer", "contact"],
                condition=Q(primary=True),
                name="single_primary_contact",
            )
        ]

    @override
    def __str__(self) -> str:
        return f"{self.customer} - {self.contact} | primary={self.primary}"
