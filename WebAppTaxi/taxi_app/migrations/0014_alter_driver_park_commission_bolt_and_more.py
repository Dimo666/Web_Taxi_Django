# Generated by Django 4.2.7 on 2023-11-24 19:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taxi_app", "0013_rename_driver_phone_boltpayment_phone_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="driver",
            name="park_commission_bolt",
            field=models.FloatField(default=13, verbose_name="Комиссия автопарка Bolt"),
        ),
        migrations.AlterField(
            model_name="driver",
            name="park_commission_uber",
            field=models.FloatField(default=11, verbose_name="Комиссия автопарка Uber"),
        ),
    ]
