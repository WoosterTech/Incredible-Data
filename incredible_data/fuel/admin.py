# ruff: noqa: F405

from django.contrib import admin

from incredible_data.fuel.models import *  # noqa: F403

# Register your models here.
admin.site.register(Manufacturer)

admin.site.register(Model)

admin.site.register(Fuel)

admin.site.register(Vehicle)

admin.site.register(FuelStation)


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "station",
        "gallons",
        "cost_per_gallon",
        "cost",
        "date_time",
    )


admin.site.register(ServiceType)

admin.site.register(ServiceLog)

admin.site.register(ServiceItem)
