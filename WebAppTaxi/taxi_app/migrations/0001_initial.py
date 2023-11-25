# Generated by Django 4.2.7 on 2023-11-16 23:19

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Driver",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        help_text="Введите имя", max_length=100, verbose_name="Имя"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        help_text="Введите фамилию",
                        max_length=100,
                        verbose_name="Фамилия",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        help_text="+421910256998",
                        max_length=15,
                        verbose_name="Номер телефона",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="index@index.com",
                        max_length=254,
                        verbose_name="Электронная почта",
                    ),
                ),
                (
                    "bank_account",
                    models.CharField(
                        help_text="IBAN: SK21 9500 0000 0023 4455 9988",
                        max_length=24,
                        verbose_name="IBAN",
                    ),
                ),
                (
                    "profile_picture",
                    models.ImageField(
                        help_text="Загрузите фото",
                        upload_to="drivers/",
                        verbose_name="Фото профиля",
                    ),
                ),
                (
                    "passport_picture",
                    models.ImageField(
                        help_text="Загрузите фото",
                        upload_to="documents/",
                        verbose_name="Фото паспорта",
                    ),
                ),
                (
                    "driver_license_picture",
                    models.ImageField(
                        help_text="Загрузите фото",
                        upload_to="documents/",
                        verbose_name="Фото водительского удостоверения",
                    ),
                ),
                (
                    "license_picture",
                    models.ImageField(
                        help_text="Загрузите фото",
                        upload_to="documents/",
                        verbose_name="Фото лицензии 'Такси'",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "make",
                    models.CharField(
                        help_text="Ведите марку автомобиля",
                        max_length=100,
                        verbose_name="Марка автомобиля",
                    ),
                ),
                (
                    "model",
                    models.CharField(
                        help_text="Ведите модель автомобиля",
                        max_length=100,
                        verbose_name="Модель автомобиля",
                    ),
                ),
                (
                    "year",
                    models.PositiveIntegerField(
                        help_text="Ведите год выпуска", verbose_name="Год выпуска"
                    ),
                ),
                (
                    "registration_number",
                    models.CharField(
                        help_text="BL753IF", max_length=10, verbose_name="ŠPZ"
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        help_text="Выберите цвет",
                        max_length=30,
                        verbose_name="Цвет автомобиля",
                    ),
                ),
                (
                    "rental_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Ведите цену аренды",
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Цена аренды",
                    ),
                ),
                (
                    "is_branded",
                    models.BooleanField(
                        default=False,
                        help_text="Автомобиль Брендирован?",
                        verbose_name="Бренд авто",
                    ),
                ),
                (
                    "technical_passport",
                    models.ImageField(
                        help_text="Загрузите фото",
                        upload_to="documents/",
                        verbose_name="Технический паспорт",
                    ),
                ),
                (
                    "car_insurance",
                    models.ImageField(
                        help_text="Загрузите фото",
                        upload_to="documents/",
                        verbose_name="Страховка автомобиля",
                    ),
                ),
                (
                    "concession",
                    models.ImageField(
                        help_text="Загрузите фото",
                        upload_to="documents/",
                        verbose_name="Лицензия машины 'Такси'",
                    ),
                ),
                (
                    "driver",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vehicle",
                        to="taxi_app.driver",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UberPayment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("week_number", models.PositiveIntegerField()),
                ("week_start", models.DateField()),
                ("week_end", models.DateField()),
                ("total_earnings", models.FloatField(default=0, verbose_name="Нетто")),
                (
                    "cash_collected",
                    models.FloatField(
                        blank=True,
                        default=0,
                        null=True,
                        verbose_name="Полученные наличные",
                    ),
                ),
                (
                    "manual_bonus",
                    models.FloatField(default=0, verbose_name="Мануальные бонусы"),
                ),
                (
                    "final_payout_uber",
                    models.FloatField(default=0, verbose_name="Финальная выплата УБЕР"),
                ),
                (
                    "driver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="uber_payments",
                        to="taxi_app.driver",
                    ),
                ),
                (
                    "vehicle",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uber_payments",
                        to="taxi_app.vehicle",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BoltPayment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("week_number", models.PositiveIntegerField()),
                ("week_start", models.DateField()),
                ("week_end", models.DateField()),
                (
                    "gross_earnings",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Брутто"
                    ),
                ),
                (
                    "cancellation_fee",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Плата за отмену",
                    ),
                ),
                (
                    "additional_charges",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Доплата",
                    ),
                ),
                (
                    "bolt_commission",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Комиссия БОЛТ"
                    ),
                ),
                (
                    "cash_collected",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Наличные",
                    ),
                ),
                (
                    "bonus",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Бонусы",
                    ),
                ),
                (
                    "compensations",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Компенсации",
                    ),
                ),
                (
                    "refunds",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Возврат заказчику",
                    ),
                ),
                (
                    "tips",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Чаявые",
                    ),
                ),
                (
                    "final_payout_bolt",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="Финальная выплата БОЛТ",
                    ),
                ),
                (
                    "driver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bolt_payments",
                        to="taxi_app.driver",
                    ),
                ),
                (
                    "driver_phone",
                    models.ForeignKey(
                        blank=True,
                        max_length=20,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="taxi_app.driver",
                        verbose_name="Телефон водителя",
                    ),
                ),
                (
                    "vehicle",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bolt_payments",
                        to="taxi_app.vehicle",
                    ),
                ),
            ],
        ),
    ]
