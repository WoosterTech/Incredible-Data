from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField

from incredible_data.fuel.geolocate import GeoLocate


# Create your models here.
class Manufacturer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Model(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.manufacturer} {self.name}"


class Fuel(models.Model):
    fuel_type = models.CharField(max_length=100)

    def __str__(self):
        return self.fuel_type


class Vehicle(models.Model):
    model = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    year = models.IntegerField()
    fuel_type = models.CharField(max_length=100)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")
    color = models.CharField(max_length=100, blank=True)
    vin = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.model} {self.year}"


class VehicleLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    mileage = models.IntegerField()
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.mileage} miles on {self.date_time}"


class FuelStation(models.Model):
    name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

    @classmethod
    def from_lat_long(cls, latitude: float, longitude: float):
        # Use a geocoding service to get the address
        location = GeoLocate.from_lat_long(latitude, longitude)
        address = location.address
        latitude = location.latitude
        longitude = location.longitude
        return cls(address=address, latitude=latitude, longitude=longitude)


class FuelLog(VehicleLog):
    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE)
    gallons = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, default=0
    )
    cost_per_gallon = MoneyField(
        max_digits=14, decimal_places=3, default_currency="USD", blank=True, default=0
    )
    cost = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", blank=True, default=0
    )
    station = models.ForeignKey(
        FuelStation, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return (
            f"{self.fuel} {self.gallons} gallons for {self.cost} on"
            f"{self.date_time:'Y-m-d'}"
        )

    def save(self, *args, **kwargs):
        self.gallons, self.cost_per_gallon, self.cost = self._calculate_missing_input()

        super().save(*args, **kwargs)

    def _calculate_missing_input(self):
        if all(
            value
            for value in [self.gallons, self.cost_per_gallon, self.cost]
            if value != 0
        ):
            return self.gallons, self.cost_per_gallon, self.cost
        input_dict = {
            "gallons": self.gallons,
            "cost_per_gallon": self.cost_per_gallon,
            "cost": self.cost,
        }
        if self.cost == 0:  # missing `cost`
            input_dict["cost"] = round(self.gallons * self.cost_per_gallon, 2)
        elif self.cost_per_gallon == 0:  # missing `cost_per_gallon`
            input_dict["cost_per_gallon"] = round(self.cost / self.gallons, 3)
        elif self.gallons == 0:  # missing `gallons`
            input_dict["gallons"] = round(self.cost / self.cost_per_gallon, 2)
        else:
            msg = "At least two of the following fields are required: gallons, cost_per_gallon, cost"  # noqa: E501
            raise ValueError(msg)

        return input_dict["gallons"], input_dict["cost_per_gallon"], input_dict["cost"]


class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class ServiceLog(VehicleLog):
    description = models.TextField()
    service_types = models.ManyToManyField(ServiceType, related_name="service_logs")
    station = models.ForeignKey(
        FuelStation, on_delete=models.SET_NULL, blank=True, null=True
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date_time} - {self.description}"


class ServiceItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")
    service_log = models.ForeignKey(
        ServiceLog, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return self.name
