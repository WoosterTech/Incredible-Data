from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Merchant, MerchantAlias


@receiver(post_save, sender=Merchant)
def add_alias(sender: models.Model, **kwargs) -> MerchantAlias:
    merchant_object = Merchant.objects.get(pk=sender.pk)
    return MerchantAlias.objects.get_or_create(
        alias=merchant_object.title, merchant_object__pk=merchant_object.pk
    )
