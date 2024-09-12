# Generated by Django 5.1.1 on 2024-09-12 23:19

import django.db.models.deletion
import django.utils.timezone
import djmoney.models.fields
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fuel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fuel_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='FuelStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('address', models.CharField(max_length=150)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('fuel_type', models.CharField(max_length=100)),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, max_digits=14)),
                ('color', models.CharField(blank=True, max_length=100)),
                ('vin', models.CharField(blank=True, max_length=100)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fuel.manufacturer')),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fuel.manufacturer')),
            ],
        ),
        migrations.CreateModel(
            name='VehicleLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mileage', models.IntegerField()),
                ('date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='fuel.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='FuelLog',
            fields=[
                ('vehiclelog_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='fuel.vehiclelog')),
                ('gallons', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=14)),
                ('cost_per_gallon_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('cost_per_gallon', djmoney.models.fields.MoneyField(blank=True, decimal_places=3, default=Decimal('0'), max_digits=14)),
                ('cost_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('cost', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=14)),
                ('fuel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fuel.fuel')),
                ('station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fuel.fuelstation')),
            ],
            bases=('fuel.vehiclelog',),
        ),
        migrations.CreateModel(
            name='ServiceLog',
            fields=[
                ('vehiclelog_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='fuel.vehiclelog')),
                ('description', models.TextField()),
                ('notes', models.TextField(blank=True)),
                ('service_types', models.ManyToManyField(related_name='service_logs', to='fuel.servicetype')),
                ('station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fuel.fuelstation')),
            ],
            bases=('fuel.vehiclelog',),
        ),
        migrations.CreateModel(
            name='ServiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, max_digits=14)),
                ('service_log', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fuel.servicelog')),
            ],
        ),
    ]
