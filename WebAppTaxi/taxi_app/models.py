from django.db import models
from django.core.validators import MinValueValidator
# Create your models here.


class Driver(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя', help_text='Введите имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', help_text='Введите фамилию')
    phone_number = models.CharField(max_length=15, help_text="+421910256998", verbose_name="Номер телефона")  # Словацкий формат
    email = models.EmailField(help_text="index@index.com", verbose_name="Электронная почта")
    bank_account = models.CharField(max_length=24, help_text="IBAN: SK21 9500 0000 0023 4455 9988", verbose_name="IBAN")  # IBAN Словацкий формат
    profile_picture = models.ImageField(upload_to='drivers/', help_text="Загрузите фото", verbose_name="Фото профиля")
    passport_picture = models.ImageField(upload_to='documents/', help_text="Загрузите фото", verbose_name="Фото паспорта")
    driver_license_picture = models.ImageField(upload_to='documents/', help_text="Загрузите фото", verbose_name="Фото водительского удостоверения")
    license_picture = models.ImageField(upload_to='documents/', help_text="Загрузите фото", verbose_name="Фото лицензии 'Такси'")
    park_commission_uber = models.FloatField(default=0.11, verbose_name="Комиссия автопарка Uber")  # Комиссия автопарка Убер
    park_commission_bolt = models.FloatField(default=0.13, verbose_name="Комиссия автопарка Bolt")  # Комиссия автопарка Болт

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vehicle(models.Model):
    driver = models.OneToOneField(
        Driver,
        related_name='vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    make = models.CharField(max_length=100, help_text="Ведите марку автомобиля", verbose_name="Марка автомобиля")  # Марка автомобиля
    model = models.CharField(max_length=100, help_text="Ведите модель автомобиля", verbose_name="Модель автомобиля") # Модель автомобиля
    year = models.PositiveIntegerField(help_text="Ведите год выпуска", verbose_name="Год выпуска")  # Год выпуска
    registration_number = models.CharField(max_length=10, help_text="BL753IF", verbose_name="ŠPZ") # Регистрационный номер
    color = models.CharField(max_length=30, help_text="Выберите цвет", verbose_name="Цвет автомобиля")  # Цвет
    rental_price = models.FloatField(default=0, validators=[MinValueValidator(0)], help_text="Ведите цену аренды", verbose_name="Цена аренды")  # Цена аренды
    is_branded = models.BooleanField(default=False, help_text="Автомобиль Брендирован?", verbose_name="Бренд авто")  # Автомобиль брендирован
    technical_passport_face = models.ImageField(upload_to='documents/', help_text="Загрузите фото", verbose_name="Технический паспорт передния сторона")  # Technický
    technical_passport_back = models.ImageField(upload_to='documents/', help_text="Загрузите фото", verbose_name="Технический паспорт задния сторона", default='ваше_значение_по_умолчанию')
    car_insurance = models.ImageField(upload_to='documents/', help_text="Загрузите фото", verbose_name="Страховка автомобиля")  # Poistenie
    concession = models.ImageField(upload_to='documents/', help_text="Загрузите фото", verbose_name="Лицензия машины 'Такси'")  # Koncesia

    def __str__(self):
        return f"{self.make} {self.model} - {self.registration_number} - {self.is_branded}"


class UberPayment(models.Model):
    driver = models.ForeignKey(Driver, related_name='uber_payments', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='uber_payments')
    week_number = models.PositiveIntegerField()  # Номер недели в году
    week_start = models.DateField()  # Начало недели
    week_end = models.DateField()  # Конец недели
    total_earnings = models.FloatField(default=0, verbose_name="Нетто") # Celkové zárobky
    cash_collected = models.FloatField(default=0, null=True, blank=True, verbose_name="Полученные наличные") # Vyplatenia : Zozbieraná hotovosť
    manual_bonus = models.FloatField(default=0, verbose_name="Мануальные бонусы") # Bonusy
    final_payout_uber = models.FloatField(default=0, verbose_name="Финальная выплата УБЕР",)


class BoltPayment(models.Model):
    driver = models.ForeignKey(Driver, related_name='bolt_payments', on_delete=models.CASCADE) # Vodič
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='bolt_payments')
    phone_number = models.ForeignKey(Driver, on_delete=models.SET_NULL, max_length=20, blank=True, null=True, verbose_name='Телефон водителя') # Vodičov telefón
    week_number = models.PositiveIntegerField()  # Номер недели в году
    week_start = models.DateField()  # Начало недели
    week_end = models.DateField()  # Конец недели
    gross_earnings = models.FloatField(default=0, verbose_name="Брутто") # Jazdné (brutto)
    cancellation_fee = models.FloatField(default=0, verbose_name="Плата за отмену") # Storno poplatok
    additional_charges = models.FloatField(default=0, verbose_name="Доплата") # Príplatok
    bolt_commission = models.FloatField(default=0, verbose_name="Комиссия БОЛТ") # Bolt Poplatok
    cash_collected = models.FloatField(default=0, verbose_name="Наличные") # Jazdy za hotovosť (vybraná hotovosť)
    bonus = models.FloatField(default=0, verbose_name="Бонусы") # Bonus
    compensations = models.FloatField(default=0, verbose_name="Компенсации") # Kompenzácie
    refunds = models.FloatField(default=0, verbose_name="Возврат заказчику") # Vratky
    tips = models.FloatField(default=0, verbose_name="Чаявые") # Sprepitné# Parkovací poplatok
    final_payout_bolt = models.FloatField(default=0, verbose_name="Финальная выплата БОЛТ")


class WeeklyReport(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='weekly_reports')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='weekly_reports')
    week_number = models.PositiveIntegerField()
    week_start = models.DateField()
    week_end = models.DateField()

    final_payout_uber = models.FloatField(default=0)
    final_payout_bolt = models.FloatField(default=0)
    total_payout = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['week_number', 'week_start', 'week_end', 'driver'],
                name='unique_weekly_report'
            )
        ]

    def __str__(self):
        return f"Weekly Report for {self.driver} - Week {self.week_number} - Total Payout: {self.total_payout}€"




# class BoltPayment(models.Model):
#     driver = models.ForeignKey(Driver, related_name='bolt_payments', on_delete=models.CASCADE) # Vodič
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='bolt_payments')
#     driver_phone = models.ForeignKey(Driver, on_delete=models.SET_NULL, max_length=20, blank=True, null=True, verbose_name='Телефон водителя') # Vodičov telefón
#     week_number = models.PositiveIntegerField()  # Номер недели в году
#     week_start = models.DateField()  # Начало недели
#     week_end = models.DateField()  # Конец недели
#     gross_earnings = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Брутто") # Jazdné (brutto)
#     cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Плата за отмену") # Storno poplatok
#     additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Доплата") # Príplatok
#     bolt_commission = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Комиссия БОЛТ") # Bolt Poplatok
#     cash_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Наличные") # Jazdy za hotovosť (vybraná hotovosť)
#     bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Бонусы") # Bonus
#     compensations = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Компенсации") # Kompenzácie
#     refunds = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Возврат заказчику") # Vratky
#     tips = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Чаявые") # Sprepitné
#     final_payout_bolt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Финальная выплата БОЛТ", validators=[MinValueValidator(Decimal('0'))])
#
#
# class UberPayment(models.Model):
#     driver = models.ForeignKey(Driver, related_name='uber_payments', on_delete=models.CASCADE)
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='uber_payments')
#     week_number = models.PositiveIntegerField()  # Номер недели в году
#     week_start = models.DateField()  # Начало недели
#     week_end = models.DateField()  # Конец недели
#     total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Нетто") # Celkové zárobky
#     cash_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True, verbose_name="Полученные наличные") # Vyplatenia : Zozbieraná hotovosť
#     manual_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Мануальные бонусы") # Bonusy
#     final_payout_uber = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Финальная выплата УБЕР", validators=[MinValueValidator(0)])


# class BoltPayment(models.Model):
#     driver = models.ForeignKey(Driver, related_name='bolt_payments', on_delete=models.CASCADE) # Vodič
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='bolt_payments')
#     driver_phone = models.ForeignKey(Driver, on_delete=models.SET_NULL, max_length=20, blank=True, null=True, verbose_name='Телефон водителя') # Vodičov telefón
#     period = models.CharField(max_length=255, help_text="Ведите неделю", verbose_name='Период') # Obdobie
#     week_number = models.PositiveIntegerField()  # Номер недели в году
#     week_start = models.DateField()  # Начало недели
#     week_end = models.DateField()  # Конец недели
#     gross_earnings = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Брутто") # Jazdné (brutto)
#     cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Плата за отмену") # Storno poplatok
#     booking_fee_payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Плата за бронирование (оплата)') # Rezervačný poplatok (platba)
#     booking_fee_deduction = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Плата за бронирование (вычет)') # Rezervačný poplatok (odpočet)
#     additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Доплата") # Príplatok
#     bolt_commission = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Комиссия БОЛТ") # Bolt Poplatok
#     cash_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Наличные") # Jazdy za hotovosť (vybraná hotovosť)
#     discounts_on_cash_jobs_covered_by_bolt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Скидки на поездки за наличные, покрытые Bolt') # Zľavy na jazdy v hotovosti hradené Bolt
#     bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Бонусы") # Bonus
#     compensations = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Компенсации") # Kompenzácie
#     refunds = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Возврат заказчику") # Vratky
#     tips = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Чаявые") # Sprepitné
#     weekly_balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Недельный баланс') # Týždenná bilancia
#     hours_online = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Часы онлайн') # Hodiny online
#     percentage_time_in_order = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Процент времени в заказе') # Percento času v objednávke
#     final_payout_bolt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Финальная выплата БОЛТ", validators=[MinValueValidator(Decimal('0'))])

#
# class UberPayment(models.Model):
#     driver_uuid = models.UUIDField()
#     driver = models.ForeignKey(Driver, related_name='uber_payments', on_delete=models.CASCADE)
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='uber_payments')
#     week_number = models.PositiveIntegerField()  # Номер недели в году
#     week_start = models.DateField()  # Начало недели
#     week_end = models.DateField()  # Конец недели
#     total_earnings = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Нетто") # Celkové zárobky
#     net_fare_earnings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Общий заработок : Чистая поездка") # Celkové zárobky : Čisté cestovné
#     refunds_and_expenses = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Возвраты и расходы") # Vrátenia peňazi a výdavky
#     payouts = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Выплаты") # Výplatenia
#     payouts_to_bank_account = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Выплаты : Перечисление на банковский счет") # Výplatenia : Výplata na bankový účet
#     cash_collected = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Полученные наличные") # Vyplatenia : Zozbieraná hotovosť
#     tips = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Чаявые") # Celkové zárobky:Prepitné
#     promo_actions = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Общий заработок: Промоакции") # Celkové zárobky:Promo akcie
#     toll_refunds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Возвраты: платные дороги") # Vrátenia peňazí a výdavky:Vrátenia peňazí:Mýto
#     manual_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Мануальные бонусы") # Bonusy
#     final_payout_uber = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Финальная выплата УБЕР", validators=[MinValueValidator(0)])





