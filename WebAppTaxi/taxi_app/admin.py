from django.contrib import admin
from .models import Driver, Vehicle, BoltPayment, UberPayment, WeeklyReport


# Register your models here.

# admin.site.register(Driver)
# admin.site.register(Vehicle)
# admin.site.register(BoltPayment)
# admin.site.register(UberPayment)
# admin.site.register(FinalPayout)

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone_number', 'email', 'bank_account', 'park_commission_bolt',
                    'park_commission_uber')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'driver', 'formatted_rental_price', 'is_branded', 'make', 'model', 'year',
                    'color')

    list_filter = ('is_branded', 'registration_number', 'driver')

    def formatted_rental_price(self, obj):
        return f"{obj.rental_price}€"
    formatted_rental_price.short_description = 'Rental Price'


@admin.register(UberPayment)
class UberPayment(admin.ModelAdmin):
    list_display = ('formatted_week_number', 'week_start', 'week_end', 'vehicle', 'driver', 'total_earnings',
                    'cash_collected', 'manual_bonus', 'final_payout_uber')

    list_filter = ('week_number', 'week_start', 'driver')

    def formatted_week_number(self, obj):
        return f"W{obj.week_number}"
    formatted_week_number.short_description = 'Week Number'


@admin.register(BoltPayment)
class BoltPayment(admin.ModelAdmin):
    list_display = ('formatted_week_number', 'week_start', 'week_end', 'driver', 'vehicle', 'gross_earnings',
                    'cancellation_fee', 'additional_charges', 'bolt_commission', 'cash_collected', 'bonus',
                    'compensations', 'refunds','tips', 'final_payout_bolt')

    list_filter = ('week_number', 'week_start', 'driver')

    def formatted_week_number(self, obj):
        return f"W{obj.week_number}"
    formatted_week_number.short_description = 'Week Number'


@admin.register(WeeklyReport)
class WeeklyReport(admin.ModelAdmin):
    list_display = ('formatted_week_number', 'week_start', 'week_end', 'driver', 'vehicle', 'final_payout_bolt',
                    'final_payout_uber', 'total_payout')

    list_filter = ('week_number', 'week_start', 'driver')

    def formatted_week_number(self, obj):
        return f"W{obj.week_number}"
    formatted_week_number.short_description = 'Week Number'
