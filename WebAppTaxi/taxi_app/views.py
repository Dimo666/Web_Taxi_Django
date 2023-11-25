import csv
from decimal import Decimal

from django.db import transaction
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Driver, BoltPayment, UberPayment, WeeklyReport
from .forms import BoltPaymentForm, UberPaymentForm
from django.http import HttpResponse
from django.db.models import Sum
import csv
from datetime import datetime


# Create your views here.


def import_uber_csv(request):
    if request.method == 'POST':
        form = UberPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            # Получаем данные из формы
            week_number = form.cleaned_data['week_number']
            week_start = form.cleaned_data['week_start']
            week_end = form.cleaned_data['week_end']
            uber_csv_file = request.FILES['uber_csv_file'].read().decode('utf-8').splitlines()
            reader = csv.DictReader(uber_csv_file, delimiter=',')

            # Создаем список для хранения созданных объектов оплаты Uber
            uber_payments = []

            # Используем Django transaction для обеспечения атомарности операции
            with transaction.atomic():
                for row in reader:
                    # print(row)
                    first_name = row['Meno vodiča']
                    last_name = row['Priezvisko vodiča']
                    uuid = row['\ufeffUUID vodiča']
                    # Получаем или создаем объект водителя
                    driver, created = Driver.objects.get_or_create(
                        first_name=first_name, last_name=last_name, uuid=uuid
                    )

                    # Собираем данные об оплате
                    uber_payment_data = {
                        'cash_collected': 0.0,  # Установите значение по умолчанию для 'cash_collected'
                        'total_earnings': 0.0  # Установите значение по умолчанию для 'total_earnings'
                    }

                    try:
                        cash_collected = float(row['Vyplatenia : Zozbieraná hotovosť'])
                        uber_payment_data['cash_collected'] = cash_collected
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'cash_collected' не может быть преобразовано в число с плавающей запятой
                        pass  # Вы можете установить другое значение по умолчанию или обработать ошибку по вашему усмотрению

                    try:
                        total_earnings = float(row['Celkové zárobky'])
                        uber_payment_data['total_earnings'] = total_earnings
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'total_earnings' не может быть преобразовано в число с плавающей запятой
                        pass  # Вы можете установить другое значение по умолчанию или обработать ошибку по вашему усмотрению

                    # Получаем или создаем объект оплаты Uber
                    uber_payment, created = UberPayment.objects.get_or_create(
                        driver=driver,
                        week_number=week_number,
                        week_start=week_start,
                        week_end=week_end,
                        defaults=uber_payment_data,
                    )

                    # Добавляем объект оплаты Uber в список
                    uber_payments.append(uber_payment)

                    # Вызываем функцию calculate_uber_payout для каждого водителя
                    calculate_uber_payout(driver.id, week_number, week_start, week_end)

            # Возвращаем ответ после обработки всех строк CSV
            return render(request, 'uber_import_success.html', {'uber_payments': uber_payments})
    else:
        form = UberPaymentForm()

    return render(request, 'uber_import.html', {'form': form})


def index(request):
    # Возвращает index.html шаблон в ответ на запрос
    return render(request, 'index.html')


def import_bolt_csv(request):
    if request.method == 'POST':
        form = BoltPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            # Получаем данные из формы
            week_number = form.cleaned_data['week_number']
            week_start = form.cleaned_data['week_start']
            week_end = form.cleaned_data['week_end']
            bolt_csv_file = request.FILES['bolt_csv_file'].read().decode('utf-8')
            lines = bolt_csv_file.splitlines()
            reader = csv.DictReader(lines[1:], delimiter=';')

            # Создаем список для хранения созданных объектов оплаты Bolt
            bolt_payments = []

            # Используем Django transaction для обеспечения атомарности операции
            with transaction.atomic():
                for row in reader:
                    # print(row)
                    # break
                    full_name = row['Vodič'].strip().split(' ')
                    # Проверяем, есть ли хотя бы два слова в full_name
                    if len(full_name) > 1:
                        first_name = full_name[0]  # Получаем имя водителя из списка
                        last_name = full_name[1]  # Получаем фамилию водителя из списка
                    elif len(full_name) == 1:  # Если только одно слово, предположим, что это имя
                        first_name = full_name[0]
                        last_name = ''  # Фамилии нет, оставляем пустую строку
                    else:  # Если нет имени, пропускаем эту строку
                        continue
                    # Получаем или создаем объект водителя
                    driver, created = Driver.objects.get_or_create(
                        first_name=first_name, last_name=last_name, phone_number=row['Vodičov telefón'].strip()
                    )
                    bolt_payments_data = {
                        'gross_earnings': 0.0,  # Установите значение по умолчанию для 'gross_earnings'
                        'cancellation_fee': 0.0,  # Установите значение по умолчанию для 'cancellation_fee'
                        'additional_charges': 0.0,  # Установите значение по умолчанию для 'additional_charges'
                        'bolt_commission': 0.0,  # Установите значение по умолчанию для 'bolt_commission'
                        'cash_collected': 0.0,  # Установите значение по умолчанию для 'cash_collected'
                        'bonus': 0.0,  # Установите значение по умолчанию для 'bonus'
                        'compensations': 0.0,  # Установите значение по умолчанию для 'compensations'
                        'refunds': 0.0,  # Установите значение по умолчанию для 'refunds'
                        'tips': 0.0,  # Установите значение по умолчанию для 'tips'
                    }

                    try:
                        gross_earnings = float(row['Jazdné (brutto)'].replace(',',
                                                                              '.'))  # Преобразование строки с доходом в число с плавающей точкой
                        bolt_payments_data['gross_earnings'] = gross_earnings
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'gross_earnings' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        cancellation_fee = float(row['Storno poplatok'].replace(',', '.'))
                        bolt_payments_data['cancellation_fee'] = cancellation_fee
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'cancellation_fee' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        additional_charges = float(row['Príplatok'].replace(',', '.'))
                        bolt_payments_data['additional_charges'] = additional_charges
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'additional_charges' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        bolt_commission = float(row['Bolt Poplatok'].replace(',', '.'))
                        bolt_payments_data['bolt_commission'] = bolt_commission
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'bolt_commission' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        cash_collected = float(row['Jazdy za hotovosť (vybraná hotovosť)'].replace(',', '.'))
                        bolt_payments_data['cash_collected'] = cash_collected
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'cash_collected' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        bonus = float(row['Bonus'].replace(',', '.'))
                        bolt_payments_data['bonus'] = bonus
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'bonus' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        compensations = float(row['Kompenzácie'].replace(',', '.'))
                        bolt_payments_data['compensations'] = compensations
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'compensations' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        refunds = float(row['Vratky'].replace(',', '.'))
                        bolt_payments_data['refunds'] = refunds
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'refunds' не может быть преобразовано в число с плавающей запятой
                        pass
                    try:
                        tips = float(row['Sprepitné'].replace(',', '.'))
                        bolt_payments_data['tips'] = tips
                    except (ValueError, TypeError):
                        # Обработка случая, когда значение 'tips' не может быть преобразовано в число с плавающей запятой
                        pass

                    # Получаем или создаем объект оплаты Bolt
                    bolt_payment, created = BoltPayment.objects.get_or_create(
                        driver=driver,
                        week_number=week_number,
                        week_start=week_start,
                        week_end=week_end,
                        defaults=bolt_payments_data,
                    )

                    # Добавляем объект оплаты Bolt в список
                    bolt_payments.append(bolt_payment)

                    # Вызываем функцию calculate_bolt_payout для каждого водителя
                    calculate_bolt_payout(driver.id, week_number, week_start, week_end)

            # Возвращаем ответ после обработки всех строк CSV
            return render(request, 'bolt_import_success.html', {'bolt_payments': bolt_payments})
    else:
        form = BoltPaymentForm()

    return render(request, 'bolt_import.html', {'form': form})


#######################################################################################################################################


def calculate_uber_payout(driver_id, week_number, week_start, week_end):
    # Получаем данные водителя и выплат за интересующий период
    driver = Driver.objects.get(id=driver_id)
    uber_payments = UberPayment.objects.filter(
        driver=driver,
        week_number=week_number,
        week_start=week_start,
        week_end=week_end
    )

    # Используем Django transaction для обеспечения атомарности операции
    with transaction.atomic():
        # Расчет выплаты для каждой записи об оплате
        for payment in uber_payments:
            # Расчет заработка с вычетом комиссии Uber
            commission_amount = payment.total_earnings * driver.park_commission_uber / 100
            earnings_after_commission = payment.total_earnings - commission_amount

            print(f"Total earnings: {payment.total_earnings}")
            print(f"Commission amount ({driver.park_commission_uber}%): {commission_amount}")
            print(f"Earnings after commission: {earnings_after_commission}")

            # Вычеты наличных
            earnings_after_deductions = earnings_after_commission + payment.cash_collected

            # Добавление бонусов
            earnings_after_deductions += payment.manual_bonus

            # Проверяем, изменилась ли финальная выплата
            if payment.final_payout_uber != earnings_after_deductions:
                print(
                    f"Updating payment Uber {driver.first_name} {driver.last_name}: {payment.final_payout_uber} -> {earnings_after_deductions}")

                # Обновление записи об оплате Uber с финальной выплатой
                payment.final_payout_uber = earnings_after_deductions
                payment.save()
                print(f"Final payout Uber: {driver.first_name, driver.last_name} - {payment.final_payout_uber}")
            else:
                print(
                    f"No update needed for payment ID {payment.id}: {payment.final_payout_uber} is already up-to-date")

    # Возвращаем список обновленных объектов оплаты Uber
    return uber_payments.aggregate(total=Sum('final_payout_uber'))['total'] or 0


def calculate_bolt_payout(driver_id, week_number, week_start, week_end):
    # Получаем данные водителя и выплат за интересующий период
    driver = Driver.objects.get(id=driver_id)
    payments = BoltPayment.objects.filter(
        driver=driver,
        week_number=week_number,
        week_start=week_start,
        week_end=week_end
    )

    with transaction.atomic():
        # Расчет оборота водителя и обновление финальной выплаты для каждой записи об оплате
        for payment in payments:
            driver_turnover = (
                    payment.gross_earnings +
                    payment.bolt_commission +
                    payment.bonus +
                    payment.tips +
                    payment.compensations +
                    payment.cancellation_fee +
                    payment.additional_charges -
                    payment.refunds
            )

            print(f"Driver turnover: {driver_turnover}")
            print(
                f"Driver commission ({driver.park_commission_bolt}%): {driver_turnover * driver.park_commission_bolt / 100}")
            print(
                f"Driver turnover after commission: {driver_turnover - driver_turnover * driver.park_commission_bolt / 100}")

            # Вычет комиссии
            commission = driver_turnover * driver.park_commission_bolt / 100

            # Сумма наличных, полученных водителем
            cash_received = payment.cash_collected

            # Финальная выплата водителю без учета аренды автомобиля
            final_payout_bolt = driver_turnover - commission + cash_received

            # Обновление записи об оплате Bolt с финальной выплатой
            payment.final_payout_bolt = Decimal(final_payout_bolt).quantize(Decimal('0.00'))
            payment.save()
            print(f"Final payout Bolt: {driver.first_name, driver.last_name} - {payment.final_payout_bolt}")

        # Рассчитываем общую сумму выплат
        total_payout = payments.aggregate(Sum('final_payout_bolt'))['final_payout_bolt__sum'] or 0
        return total_payout


def calculate_total_payout(driver_id, week_number, week_start, week_end):
    driver = Driver.objects.get(id=driver_id)

    # Инициализируем стоимость аренды автомобиля нулём по умолчанию.
    vehicle_rental = 0

    # Проверяем, есть ли у водителя связанный автомобиль и арендуется ли он.
    if hasattr(driver, 'vehicle') and driver.vehicle and driver.vehicle.is_rented:
        vehicle_rental = driver.vehicle.rental_price

    # Рассчитываем общий доход от Uber и Bolt.
    uber_total = calculate_uber_payout(driver_id, week_number, week_start, week_end) or 0
    bolt_total = calculate_bolt_payout(driver_id, week_number, week_start, week_end) or 0

    # Вычитаем стоимость аренды автомобиля из общей выплаты, если это применимо.
    total_payout = uber_total + bolt_total - vehicle_rental
    print(f"Total payout Bolt and Uber: {driver.first_name} {driver.last_name} - {total_payout}")

    # Обновляем или создаём запись в WeeklyReport.
    with transaction.atomic():
        weekly_report, created = WeeklyReport.objects.update_or_create(
            driver=driver,
            week_number=week_number,
            week_start=week_start,
            week_end=week_end,
            defaults={
                'final_payout_uber': uber_total,
                'final_payout_bolt': bolt_total,
                'total_payout': total_payout
            }
        )

    return weekly_report


@csrf_exempt
def calculate_total_payout_for_all_drivers_view(request):
    if request.method == 'POST':
        week_number = request.POST.get('week_number')
        week_start = request.POST.get('week_start')
        week_end = request.POST.get('week_end')

        drivers = Driver.objects.all()
        for driver in drivers:
            calculate_total_payout(driver.id, week_number, week_start, week_end)

        # После выполнения расчета для всех водителей, верните подтверждение
        return HttpResponse("Total payouts have been calculated.")

    # Если GET запрос, просто отобразите форму
    return render(request, 'calculate_total_payout_for_all_drivers.html')


@csrf_exempt  # Этот декоратор используйте с осторожностью
def calculate_payout_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        week_number = request.POST.get('week_number')
        week_start = request.POST.get('week_start')
        week_end = request.POST.get('week_end')

        # Находим водителя по имени и фамилии
        try:
            driver = Driver.objects.get(first_name=first_name, last_name=last_name)
        except Driver.DoesNotExist:
            return HttpResponse("Driver not found.", status=404)
        except Driver.MultipleObjectsReturned:
            return HttpResponse("Multiple drivers found. Please be more specific.", status=400)

        # Вызов функции для расчета выплаты
        weekly_report = calculate_total_payout(driver.id, week_number, week_start, week_end)

        # Отображаем результат
        return HttpResponse(f"Total payout for {first_name} {last_name} is: {weekly_report.total_payout}")

    # Если GET запрос, отображаем форму
    return render(request, 'calculate_payout.html')


# Эта функция теперь просто вызывает create_payment_report_for_week
def create_payment_report(week_number):
    return create_payment_report_for_week(week_number)


def export_payment_report_to_csv(request, week_number):
    # Получаем отчеты за указанную неделю
    payment_report = create_payment_report_for_week(week_number)

    # Если отчеты найдены, используем даты из первой записи для названия файла
    if payment_report:
        week_start = payment_report[0]['week_start']
        week_end = payment_report[0]['week_end']
        filename = f"payment_report_week_{week_number}_{week_start}_to_{week_end}.csv"
    else:
        # Если отчетов нет, используем текущую дату для названия файла
        date_now = datetime.now().strftime('%Y-%m-%d')
        filename = f"payment_report_{date_now}.csv"

    # Создаем HTTP-ответ с соответствующим CSV-заголовком
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )

    # Создаем CSV-писатель с использованием этого HTTP-ответа
    writer = csv.writer(response)

    # Записываем заголовки для CSV
    writer.writerow(
        ['Driver Name', 'Phone Number', 'Week Number', 'Week Start', 'Week End', 'Bank Account', 'Total Payout'])

    # Записываем данные отчета
    for report in payment_report:
        writer.writerow([
            report['driver_name'],
            report['phone_number'],
            report['week_number'],
            report['week_start'],
            report['week_end'],
            report['bank_account'],
            report['total_payout']
        ])

    return response


# Вью для экспорта отчета в CSV
def payment_report_csv_view(request):
    week_number = request.GET.get('week_number')
    if not week_number:
        return HttpResponse("Week number is required", status=400)

    return export_payment_report_to_csv(request, week_number)


def payment_report_form_view(request):
    return render(request, 'payment_report_form.html')


# Обновленная функция для создания отчета за определенную неделю
def create_payment_report_for_week(week_number):
    # Получаем отчеты за указанную неделю
    weekly_reports = WeeklyReport.objects.filter(week_number=week_number)

    payment_report = [{
        'driver_name': f"{report.driver.first_name} {report.driver.last_name}",
        'phone_number': report.driver.phone_number,
        'week_number': week_number,
        'week_start': report.week_start,
        'week_end': report.week_end,
        'bank_account': report.driver.bank_account,
        'total_payout': report.total_payout
    } for report in weekly_reports]

    return payment_report


# Функция для отображения формы и генерации отчета
def payment_report_html_view(request):
    week_number = request.GET.get('week_number')
    payment_report = []

    if week_number:
        payment_report = create_payment_report_for_week(week_number)

    context = {
        'payment_report': payment_report,
        'week_number': week_number,  # Добавляем номер недели в контекст
    }

    return render(request, 'payment_report.html', context)
