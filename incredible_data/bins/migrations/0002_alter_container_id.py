# Generated by Django 5.0.3 on 2024-03-24 18:22

import incredible_data.bins.models.bins_container_models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bins', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='id',
            field=models.UUIDField(default=incredible_data.bins.models.bins_container_models.short_uuid, primary_key=True, serialize=False),
        ),
    ]