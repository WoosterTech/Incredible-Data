# Generated by Django 5.0.4 on 2024-04-17 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0002_invoice_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='number',
            field=models.CharField(editable=False, max_length=10, verbose_name='invoice number'),
        ),
    ]
