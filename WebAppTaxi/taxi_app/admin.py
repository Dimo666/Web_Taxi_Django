from django.contrib import admin
from django.utils.html import format_html

from . import models
from .models import Driver, Vehicle, BoltPayment, UberPayment, WeeklyReport


# Register your models here.

# admin.site.register(Driver)
# admin.site.register(Vehicle)
# admin.site.register(BoltPayment)
# admin.site.register(UberPayment)
# admin.site.register(FinalPayout)

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name', 'vehicle', 'phone_number', 'email', 'bank_account', 'park_commission_bolt',
        'park_commission_uber')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email', 'bank_account')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'driver', 'formatted_rental_price', 'is_branded', 'make', 'model', 'year',
                    'color')

    list_filter = ('is_branded', 'registration_number', 'driver')
    search_fields = ('registration_number', 'driver__first_name', 'driver__last_name')

    def formatted_rental_price(self, obj):
        return f"{obj.rental_price}€"

    formatted_rental_price.short_description = 'Rental Price'


@admin.register(UberPayment)
class UberPayment(admin.ModelAdmin):
    list_display = (
        'formatted_week_number', 'week_start', 'week_end', 'get_vehicle_registration_number', 'driver',
        'total_earnings',
        'cash_collected', 'manual_bonus', 'final_payout_uber')

    list_filter = ('week_number', 'week_start', 'driver')
    search_fields = ('driver__first_name', 'driver__last_name')

    def formatted_week_number(self, obj):
        return f"W{obj.week_number}"

    formatted_week_number.short_description = 'Week Number'

    def get_vehicle_registration_number(self, obj):
        if obj.driver and obj.driver.vehicle:
            return obj.driver.vehicle.registration_number
        return "N/A"

    get_vehicle_registration_number.short_description = 'Registration Number'


@admin.register(BoltPayment)
class BoltPayment(admin.ModelAdmin):
    list_display = (
        'formatted_week_number', 'week_start', 'week_end', 'driver', 'get_vehicle_registration_number',
        'gross_earnings',
        'cancellation_fee', 'additional_charges', 'bolt_commission', 'cash_collected', 'bonus',
        'compensations', 'refunds', 'tips', 'final_payout_bolt')

    list_filter = ('week_number', 'week_start', 'driver')
    search_fields = ('driver__first_name', 'driver__last_name')

    def formatted_week_number(self, obj):
        return f"W{obj.week_number}"

    formatted_week_number.short_description = 'Week Number'

    def get_vehicle_registration_number(self, obj):
        if obj.driver and obj.driver.vehicle:
            return obj.driver.vehicle.registration_number
        return "N/A"

    get_vehicle_registration_number.short_description = 'Registration Number'


@admin.register(WeeklyReport)
class WeeklyReport(admin.ModelAdmin):
    list_display = (
        'formatted_week_number', 'week_start', 'week_end', 'driver', 'get_vehicle_registration_number',
        'get_rental_price',
        'final_payout_bolt',
        'final_payout_uber', 'total_payout')

    list_filter = ('week_number', 'week_start', 'driver')
    search_fields = ('driver__first_name', 'driver__last_name')

    def formatted_week_number(self, obj):
        return f"W{obj.week_number}"

    formatted_week_number.short_description = 'Week Number'

    def get_rental_price(self, obj):
        # Проверяем, есть ли у водителя связанный автомобиль
        if obj.driver and obj.driver.vehicle:
            # Возвращаем цену аренды автомобиля
            return obj.driver.vehicle.rental_price
        return "N/A"  # Если у водителя нет связанного автомобиля, возвращаем "N/A"

    get_rental_price.short_description = 'Rental Price'
    get_rental_price.admin_order_field = 'driver__vehicle__rental_price'  # Позволяет сортировать по этому полю в админке

    def get_vehicle_registration_number(self, obj):
        if obj.driver and obj.driver.vehicle:
            return obj.driver.vehicle.registration_number
        return "N/A"

    get_vehicle_registration_number.short_description = 'Registration Number'
