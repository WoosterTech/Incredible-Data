from typing import TYPE_CHECKING, final, override

from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel

from incredible_data.contacts.models.utility_models import UserStampedModel

# Create your models here.
if TYPE_CHECKING:
    from incredible_data.contacts.models.contacts_models import Contact, PhoneNumber


@final
class Customer(TimeStampedModel, UserStampedModel):
    name = models.CharField(_("customer"), max_length=100)
    main_phone: "models.ForeignKey[PhoneNumber | None]" = models.ForeignKey(
        "contacts.PhoneNumber",
        verbose_name=_("organization phone"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    contacts: "models.ManyToManyField[PhoneNumber, models.Model]" = (
        models.ManyToManyField(
            "contacts.Contact", verbose_name=_("contacts"), through="CustomerContact"
        )
    )
    slug = AutoSlugField(populate_from="name")  # pyright: ignore[reportCallIssue]

    if TYPE_CHECKING:
        customercontact_set: "models.QuerySet[CustomerContact]"  # pyright: ignore[reportUninitializedInstanceVariable]

    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ["name"]

    @override
    def __str__(self) -> str:
        return self.name

    @property
    def primary_contact(self) -> "Contact | None":
        """
        Returns the primary contact for this customer, if it exists.
        """

        try:
            return self.customercontact_set.get(primary=True).contact
        except CustomerContact.DoesNotExist:
            return None

    def get_absolute_url(self):
        return reverse("customers:customer-detail", kwargs={"slug": self.slug})  # pyright: ignore[reportUnknownMemberType]

    def get_create_order_url(self):
        return reverse("business:order-create") + f"?customer={self.pk}"  # pyright: ignore[reportAny]


@final
class CustomerContact(models.Model):
    customer = models.ForeignKey(
        Customer, verbose_name=_("customer"), on_delete=models.CASCADE
    )
    contact: "models.ForeignKey[Contact]" = models.ForeignKey(
        "contacts.Contact", verbose_name=_("contact"), on_delete=models.CASCADE
    )
    primary = models.BooleanField(_("primary"), default=False)

    @final
    class Meta:
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
