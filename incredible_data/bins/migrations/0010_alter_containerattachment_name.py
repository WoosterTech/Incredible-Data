# Generated by Django 5.0.6 on 2024-06-12 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bins', '0009_fix_attachment_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='containerattachment',
            name='name',
            field=models.CharField(blank=True, help_text='should auto-populate on save', max_length=50, verbose_name='name'),
        ),
    ]
