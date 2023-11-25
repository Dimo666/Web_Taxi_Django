"""
URL configuration for main_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from taxi_app import views
from taxi_app.views import calculate_total_payout_for_all_drivers_view, payment_report_csv_view, \
    payment_report_html_view, payment_report_form_view

# from taxi_app.views import payment_report_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('uber_import/', views.import_uber_csv, name='import_uber_csv'),
    path('bolt_import/', views.import_bolt_csv, name='import_bolt_csv'),
    path('calculate_payout/', views.calculate_payout_view, name='calculate_payout'),
    path('calculate_payouts_all/', calculate_total_payout_for_all_drivers_view,
         name='calculate_total_payout_for_all_drivers'),
    path('payment_report_form/', payment_report_form_view, name='payment_report_form'),
    path('payment_report/', payment_report_html_view, name='payment_report_html'),
    path('payment_report/csv/', payment_report_csv_view, name='payment_report_csv'),
]
