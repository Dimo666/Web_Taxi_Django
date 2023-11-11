import csv
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render

from taxi_app.models import Driver, BoltPayment, UberPayment
from django.db.models import Sum, F, DecimalField

# Create your views here.


def import_bolt_payments(csv_file_path):
    with open(csv_file_path, encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')  # Указываем делитель, если он отличается от запятой
        for row in reader:
            # Извлекаем имя и фамилию, предполагая, что последнее слово - это фамилия
            *first_names, last_name = row['Vodič'].rsplit(maxsplit=1)
            first_name = ' '.join(first_names)

            # Найти водителя или создать нового, если он не найден
            driver, created = Driver.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'phone_number': row['Vodičov telefón']}
            )

            # Определение периода из CSV
            period = row['Obdobie']

            # Преобразование данных о доходах и проверка на уникальность периода
            try:
                gross_earnings = float(row['Jazdné (brutto)'].replace(',', '.'))
            except ValueError:
                # Логирование или обработка ошибок преобразования данных
                continue

            # Подготовить данные для создания объекта BoltPayment
            bolt_payment_data = {
                'driver': driver,
                'period': row['Obdobie'],
                'gross_earnings': row['Jazdné (brutto)'].replace(',', '.'),
                'cancellation_fee': row['Storno poplatok'].replace(',', '.'),
                'booking_fee_payment': row['Rezervačný poplatok (platba)'].replace(',', '.'),
                'booking_fee_deduction': row['Rezervačný poplatok (odpočet)'].replace(',', '.'),
                'additional_charges': row['Príplatok'].replace(',', '.'),
                'bolt_commission': row['Bolt Poplatok'].replace(',', '.'),
                'cash_collected': row['Jazdy za hotovosť (vybraná hotovosť)'].replace(',', '.'),
                'discounts_on_cash_jobs_covered_by_bolt': row['Zľavy na jazdy v hotovosti hradené Bolt'].replace(',', '.'),
                'bonus': row['Bonus'].replace(',', '.'),
                'compensations': row['Kompenzácie'].replace(',', '.'),
                'refunds': row['Vratky'].replace(',', '.'),
                'tips': row['Sprepitné'].replace(',', '.'),
                'weekly_balance': row['Týždenná bilancia'].replace(',', '.'),
                'hours_online': row['Hodiny online'].replace(',', '.'),
                'percentage_time_in_order': row['Percento času v objednávke'].replace(',', '.'),

                # Продолжить с остальными полями, соответствующими модели BoltPayment
            }

            # Использовать transaction.atomic для предотвращения частичного импорта данных
            with transaction.atomic():
                # Создать платеж Bolt, если он еще не существует для данного водителя и периода
                bolt_payment, bp_created = BoltPayment.objects.get_or_create(
                    driver=driver,
                    period=row['Obdobie'],
                    defaults=bolt_payment_data
                )

                if not created:
                    # Если запись для данного водителя и периода уже существует, пропустим её
                    print(f"Record for {driver} for period {period} already exists.")
                    continue

                    # Здесь добавляется логика для обновления или добавления дополнительных данных в bolt_payment, если это необходимо


def calculate_bolt_payout(driver_id):
    # Получаем данные водителя и выплат за интересующий период
    driver = Driver.objects.get(id=driver_id)
    payments = BoltPayment.objects.filter(driver=driver)

    # Расчет оборота водителя
    driver_turnover = sum(
        (payment.gross_earnings - payment.bolt_commission + payment.bonus +
         payment.tips + payment.compensations + payment.cancellation_fee +
         payment.additional_charges - payment.refunds) for payment in payments
    )

    # Вычет комиссии
    commission = driver_turnover * 0.10  # 10% комиссии

    # Сумма наличных, полученных водителем
    cash_received = sum(payment.cash_collected for payment in payments)

    # Аренда автомобиля
    vehicle = sum(payment.vehicle.rental_price for payment in payments)

    # Финальная выплата водителю
    final_payout_bolt = driver_turnover - commission - cash_received - vehicle

    return final_payout_bolt


def calculate_uber_payout(driver_id, final_payout_uber=None):
    # Получаем данные водителя и выплат за интересующий период
    driver = Driver.objects.get(id=driver_id)
    uber_payments = UberPayment.objects.filter(driver=driver)

    # Переменная для хранения итоговой выплаты
    final_payout_uber = 0

    # Расчет выплаты для каждой записи об оплате
    for payment in uber_payments:
        # Расчет заработка с вычетом комиссии Uber
        earnings_after_commission = payment.total_earnings * 0.90  # Вычет 10% комиссии

        # Вычеты выплат и аренды авто
        earnings_after_deductions = (earnings_after_commission - payment.cash_collected - payment.vehicle.rental_price)

        # Добавление бонусов
        earnings_after_deductions += payment.manual_bonus

        # Обновление итоговой выплаты
        final_payout_uber += earnings_after_deductions

    return final_payout_uber


def calculate_total_payout(driver_id):
    driver = Driver.objects.get(id=driver_id)

    # Суммируем итоговые выплаты от Bolt
    bolt_total = driver.bolt_payments.aggregate(
        total_payout=Sum('final_payout_bolt')
    )['total_payout'] or 0  # Используем 0, если результат None

    # Суммируем итоговые выплаты от Uber
    uber_total = driver.uber_payments.aggregate(
        total_payout=Sum('final_payout_uber')
    )['total_payout'] or 0  # Используем 0, если результат None

    # Итоговая выплата водителю от Bolt и Uber
    total_payout = bolt_total + uber_total

    return total_payout


def create_payment_report():
    # Получаем всех водителей
    drivers = Driver.objects.all()

    # Словарь для хранения отчета
    payment_report = []

    # Создаем отчет по каждому водителю
    for driver in drivers:
        driver_total_payout = calculate_total_payout(driver.id)
        payment_report.append({
            'driver_name': f"{driver.first_name} {driver.last_name}",
            'phone_number': driver.phone_number,
            'bank_account': driver.bank_account,  # Получаем банковский счет водителя
            'total_payout': driver_total_payout
        })

    # Возвращаем отчет
    return payment_report


def export_payment_report_to_csv(payment_report):
    # Создаем HTTP-ответ с соответствующим CSV-заголовком
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="payment_report.csv"'},
    )

    # Создаем CSV-писатель с использованием этого HTTP-ответа
    writer = csv.writer(response)

    # Записываем заголовки для CSV
    writer.writerow(['Driver Name', 'Phone Number', 'Bank Account', 'Total Payout'])

    # Записываем данные отчета
    for report in payment_report:
        writer.writerow([
            report['driver_name'],
            report['phone_number'],
            report['bank_account'],  # Добавляем банковский счет
            report['total_payout']
        ])

    # Возвращаем HTTP-ответ, который будет содержать CSV-файл
    return response


# Эта функция используется в Django view для создания экспорта
def payment_report_view(request):
    # Создаем отчет
    payment_report = create_payment_report()

    # Экспортируем отчет в CSV
    return export_payment_report_to_csv(payment_report)



