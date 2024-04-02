from django.contrib import admin

from incredible_data.contacts.models import Contact, Email, PhoneNumber
from incredible_data.customers.admin import UserStampedModelAdmin


# Register your models here.
@admin.register(Contact)
class ContactAdmin(UserStampedModelAdmin):
    list_display = ["full_name"]


@admin.register(Email)
class EmailAdmin(UserStampedModelAdmin):
    list_display = ["contact", "email"]


@admin.register(PhoneNumber)
class PhoneNumberAdmin(UserStampedModelAdmin):
    list_display = ["contact", "number"]
