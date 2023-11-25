import csv
from django.db import transaction
from django.shortcuts import render, redirect

from .models import Driver, BoltPayment, UberPayment
from .forms import BoltPaymentForm, UberPaymentForm
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
import logging
from decimal import Decimal

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
                    first_name = row['Meno vodiča']
                    last_name = row['Priezvisko vodiča']
                    # Получаем или создаем объект водителя
                    driver, created = Driver.objects.get_or_create(
                        first_name=first_name, last_name=last_name
                    )

                    # Собираем данные об оплате
                    uber_payment_data = {
                        'total_earnings': float(row['Celkové zárobky']),  # Заменяем запятую на точку, если это формат числа с плавающей запятой
                        'cash_collected': float(row['Vyplatenia : Zozbieraná hotovosť'])
                    }

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


            # Возвращаем ответ после обработки всех строк CSV
            return render(request, 'uber_import_success.html', {'uber_payments': uber_payments})
    else:
        form = UberPaymentForm()

    return render(request, 'uber_import.html', {'form': form})


def index(request):
    # Возвращает index.html шаблон в ответ на запрос
    return render(request, 'index.html')


@require_http_methods(["POST"])
def import_bolt_payments_view(request):
    # Создаем экземпляр формы с данными POST и файлами
    form = BoltPaymentForm(request.POST, request.FILES)

    # Проверяем, что форма заполнена корректно
    if form.is_valid():
        # Получаем файл из формы. Используем метод .get() на словаре,
        # чтобы избежать ошибок, если 'bolt_csv' не существует в request.FILES
        csv_file = request.FILES.get('bolt_csv')

        # Проверяем, что файл действительно был загружен
        if csv_file:
            # Получаем остальные данные из формы
            week_number = form.cleaned_data['week_number']
            week_start = form.cleaned_data['week_start']
            week_end = form.cleaned_data['week_end']

            # Передаем файл и данные в функцию обработки CSV
            result_message = import_bolt_payments(csv_file, week_number, week_start, week_end)

            # Возвращаем результат обработки клиенту
            return HttpResponse(result_message)
        else:
            # Возвращаем ошибку, если файл не был загружен
            return JsonResponse({'error': 'Файл не был загружен.'}, status=400)
    else:
        # Возвращаем ошибку, если данные формы некорректны
        return JsonResponse({'error': 'Неверные данные формы.'}, status=400)


# def preprocess_csv_data(file_data):
#     # Разбиваем файл на строки
#     lines = file_data.split('\n')
#
#     # Обрабатываем строки для исправления кавычек
#     processed_lines = []
#     for line in lines:
#         # Удаляем ведущие и замыкающие кавычки
#         line = line.strip('"')
#         # Заменяем двойные кавычки на одинарные
#         line = line.replace('""', '"')
#         processed_lines.append(line)
#
#     # Соединяем обработанные строки обратно в одну строку
#     return '\n'.join(processed_lines)

#
# Функция для импорта данных из CSV файла
def import_bolt_payments(uploaded_file, week_number, week_start, week_end):
    # Настраиваем логирование
    logger = logging.getLogger('bolt_import.log')

    # Используем логгер
    logger.debug('Это сообщение отладки')
    logger.info('Это информационное сообщение')
    logger.warning('Это предупреждение')
    logger.error('Это сообщение об ошибке')
    logger.critical('Это критическое сообщение')

    # Счетчики для отслеживания успешных и неудачных операций
    success_count = 0
    fail_count = 0

    # Обрабатываем файл
    # Вместо чтения файла с диска мы читаем данные непосредственно из загруженного файла
    file_data = uploaded_file.read().decode('utf-8-sig')
    # processed_file_data = preprocess_csv_data(file_data)
    # csv_data = io.StringIO(processed_file_data)
    # reader = csv.DictReader(csv_data, delimiter=',')
    reader = csv.DictReader(file_data.splitlines(), delimiter=',')
    for row in reader:
        try:
            if 'Vodič' not in row:
                logger.error(f"Ключ 'Vodič' не найден в строке: {row}")
                fail_count += 1
                continue
            with transaction.atomic():
                full_name = row['Vodič'].strip().split(' ')
                if full_name:  # Проверяем, есть ли данные в списке
                    first_name = full_name[0]
                    last_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''
                    # ...
                else:
                    logger.error(f"Поле 'Vodič' пустое для строки: {row}")
                    continue  # Пропускаем эту строку и переходим к следующей

                # Поиск или создание объекта водителя
                driver, created = Driver.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={'phone_number': row.get('Vodičov telefón', '')}
                )

                # Создание или обновление записи о платеже
                bolt_payment, created = BoltPayment.objects.update_or_create(
                    driver=driver,
                    period=row['Obdobie'],
                    defaults={
                        'week_number': week_number,
                        'week_start': week_start,
                        'week_end': week_end,
                        'gross_earnings': row['Jazdné (brutto)'].replace(',', '.'),
                        'cancellation_fee': row['Storno poplatok'].replace(',', '.'),
                        'booking_fee_payment': row['Rezervačný poplatok (platba)'].replace(',', '.'),
                        'booking_fee_deduction': row['Rezervačný poplatok (odpočet)'].replace(',', '.'),
                        'additional_charges': row['Príplatok'].replace(',', '.'),
                        'bolt_commission': row['Bolt Poplatok'].replace(',', '.'),
                        'cash_collected': row['Jazdy za hotovosť (vybraná hotovosť)'].replace(',', '.'),
                        'discounts_on_cash_jobs_covered_by_bolt': row['Zľavy na jazdy v hotovosti hradené Bolt '].replace(',', '.'),
                        'bonus': row['Bonus'].replace(',', '.'),
                        'compensations': row['Kompenzácie'].replace(',', '.'),
                        'refunds': row['Vratky'].replace(',', '.'),
                        'tips': row['Sprepitné'].replace(',', '.'),
                        'weekly_balance': row['Týždenná bilancia'].replace(',', '.'),
                        'hours_online': row['Hodiny online'].replace(',', '.'),
                        'percentage_time_in_order': row['Percento času v objednávke'].replace(',', '.'),
                        # ... другие поля из вашего CSV
                    }
                )

            # Если все прошло успешно, увеличиваем счетчик успешных операций
            success_count += 1

        except ValidationError as e:
            # Если возникают ошибки валидации, логируем их и увеличиваем счетчик ошибок
            logger.error(f"ValidationError: {e} для строки {row}")
            fail_count += 1
        except Exception as e:
            # Логирование любых других исключений
            logger.error(f"Неожиданная ошибка: {e} для строки {row}")
            fail_count += 1

    # Возвращаем сообщение с результатами операции
    return f"Импорт завершен. Успешно: {success_count}, Ошибок: {fail_count}."



###########################################################################################################
# def import_bolt_payments(csv_file, week_number, week_start, week_end):
#     # Создаем логгер с именем 'django', который был определен в настройках
#     logger = logging.getLogger('bolt_import.log')
#
#     # Используем логгер
#     logger.debug('Это сообщение отладки')
#     logger.info('Это информационное сообщение')
#     logger.warning('Это предупреждение')
#     logger.error('Это сообщение об ошибке')
#     logger.critical('Это критическое сообщение')
#
#     success_count = 0  # Счетчик успешно импортированных записей
#     fail_count = 0  # Счетчик записей, импорт которых не удался
#
#     with open(csv_file, encoding='utf-8') as csv_file:
#         reader = csv.DictReader(csv_file, delimiter=';')
#         for row in reader:
#             try:
#                 # Разбор имени водителя на имя и фамилию
#                 *first_names, last_name = row['Vodič'].rsplit(maxsplit=1)
#                 first_name = ' '.join(first_names)
#                 # Создаем или получаем объект водителя из базы данных
#                 driver, _ = Driver.objects.get_or_create(
#                     first_name=first_name,
#                     last_name=last_name,
#                     defaults={'phone_number': row['Vodičov telefón']}
#                 )
#
#                 # Определение периода из CSV
#                 period = row['Obdobie']
#
#                 try:
#                     # Преобразование строки с доходом в число с плавающей точкой
#                     gross_earnings = float(row['Jazdné (brutto)'].replace(',', '.'))
#                 except ValueError:
#                     # Логируем ошибку, если преобразование не удалось
#                     logger.error(f"ValueError: Невозможно преобразовать доход для {first_name} {last_name}")
#                     fail_count += 1
#                     continue
#
#                 bolt_payment_data = {
#                     'driver': driver,
#                     'week_number': week_number,  # Получаем номер недели
#                     'week_start': week_start,  # Получаем начало недели
#                     'week_end': week_end,  # Получаем конец недели
#                     'period': row['Obdobie'],
#                     'gross_earnings': row['Jazdné (brutto)'].replace(',', '.'),
#                     'cancellation_fee': row['Storno poplatok'].replace(',', '.'),
#                     'booking_fee_payment': row['Rezervačný poplatok (platba)'].replace(',', '.'),
#                     'booking_fee_deduction': row['Rezervačný poplatok (odpočet)'].replace(',', '.'),
#                     'additional_charges': row['Príplatok'].replace(',', '.'),
#                     'bolt_commission': row['Bolt Poplatok'].replace(',', '.'),
#                     'cash_collected': row['Jazdy za hotovosť (vybraná hotovosť)'].replace(',', '.'),
#                     'discounts_on_cash_jobs_covered_by_bolt': row['Zľavy na jazdy v hotovosti hradené Bolt'].replace(',', '.'),
#                     'bonus': row['Bonus'].replace(',', '.'),
#                     'compensations': row['Kompenzácie'].replace(',', '.'),
#                     'refunds': row['Vratky'].replace(',', '.'),
#                     'tips': row['Sprepitné'].replace(',', '.'),
#                     'weekly_balance': row['Týždenná bilancia'].replace(',', '.'),
#                     'hours_online': row['Hodiny online'].replace(',', '.'),
#                     'percentage_time_in_order': row['Percento času v objednávke'].replace(',', '.'),
#                 }
#
#                 with transaction.atomic():
#                     # Создаем или получаем объект платежа, связанный с водителем и периодом
#                     bolt_payment, created = BoltPayment.objects.get_or_create(
#                         driver=driver,
#                         period=period,
#                         defaults=bolt_payment_data
#                     )
#
#                     if not created:
#                         # Если объект уже существует, обновляем его данными из CSV
#                         bolt_payment.update(**bolt_payment_data)
#                         logger.info(f"Обновлена существующая запись BoltPayment для {driver} за период {period}.")
#
#                     success_count += 1
#
#             except ValidationError as e:
#                 # Обработка ошибок валидации данных модели Django
#                 logger.error(f"ValidationError: {e} для строки {row}")
#                 fail_count += 1
#                 continue
#             except Exception as e:
#                 # Обработка всех других исключений
#                 logger.error(f"Неожиданная ошибка: {e} для строки {row}")
#                 fail_count += 1
#                 continue
#
#     # Возврат сообщения о результате импорта
#     return f"Импорт завершен с {success_count} успешными импортами и {fail_count} ошибками."
############################################################################## #############################################


# @require_http_methods(["POST"])
# def import_uber_payments_view(request):
#     # Создаем экземпляр формы с данными POST и файлами
#     form = UberPaymentForm(request.POST, request.FILES)
#
#     # Проверяем, что форма заполнена корректно
#     if form.is_valid():
#         # Получаем файл из формы. Используем метод .get() на словаре,
#         # чтобы избежать ошибок, если 'uber_csv' не существует в request.FILES
#         csv_file = request.FILES.get('uber_csv')
#
#         # Проверяем, что файл действительно был загружен
#         if csv_file:
#             # Получаем остальные данные из формы
#             week_number = form.cleaned_data['week_number']
#             week_start = form.cleaned_data['week_start']
#             week_end = form.cleaned_data['week_end']
#
#
#             # Передаем файл и данные в функцию обработки CSV
#             result_message = import_uber_payments(csv_file, week_number, week_start, week_end)
#
#             # Возвращаем результат обработки клиенту
#             return HttpResponse(result_message)
#         else:
#             # Возвращаем ошибку, если файл не был загружен
#             return JsonResponse({'error': 'Файл не был загружен.'}, status=400)
#     else:
#         # Возвращаем ошибку, если данные формы некорректны
#         return JsonResponse({'error': 'Неверные данные формы.'}, status=400)
#
#
# def import_uber_payments(csv_file, week_start, week_end, week_number):
#     # Создаем логгер с именем 'uber_logger', который был определен в настройках
#     logger = logging.getLogger('uber_import.log')
#
#     # Используйте logger для записи логов
#     logger.info('Начало импорта данных Uber')
#
#     # Счетчики
#     success_count = 0
#     fail_count = 0
#
#     try:
#         # Обработка CSV файла, который является файлоподобным объектом
#         reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
#
#         for row in reader:
#             try:
#                 first_name = row['Meno vodiča']
#                 last_name = row['Priezvisko vodiča']
#
#                 # Создаем или получаем объект водителя
#                 driver, created = Driver.objects.get_or_create(
#                     first_name=first_name, last_name=last_name
#                 )
#
#                 # Собираем данные для записи
#                 uber_payment_data = {
#                     'driver': driver,
#                     'week_start': week_start,
#                     'week_end': week_end,
#                     'week_number': week_number,  # Добавляем номер недели
#                     # 'driver_uuid': row['UID vodiča'],
#                     'total_earnings': Decimal(row['Celkové zárobky'].replace(',', '.')),
#                     # 'net_fare_earnings': Decimal(row['Celkové zárobky : Čisté cestovné'].replace(',', '.')),
#                     # 'refunds_and_expenses': Decimal(row['Vrátenia peňazi a výdavky'].replace(',', '.')),
#                     # 'payouts': Decimal(row['Výplatenia'].replace(',', '.')),
#                     # 'payouts_to_bank_account': Decimal(row['Vyplatenia : Prevedené на bankový účet'].replace(',', '.')),
#                     'cash_collected': Decimal(row['Vyplatenia : Zozbieraná hotovosť'].replace(',', '.')),
#                     # 'tips': Decimal(row['Celkové zárobky:Prepitné'].replace(',', '.')),
#                     # 'promo_actions': Decimal(row['Celkové zárobky:Promo akcie'].replace(',', '.')),
#                     # 'toll_refunds': Decimal(row['Vrátenia peňazí a výдavky:Vrátenия peňazí:Mýto'].replace(',', '.')),
#                     # ... добавление и преобразование остальных полей ...
#                 }
#
#                 # Атомарное создание или обновление записи
#                 with transaction.atomic():
#                     uber_payment, created = UberPayment.objects.get_or_create(
#                         driver=driver,
#                         week_start=week_start,
#                         defaults=uber_payment_data
#                     )
#                     if not created:
#                         logger.info(f"Обновление существующей записи: {driver} за период {week_start} - {week_end}")
#                         for attr, value in uber_payment_data.items():
#                             setattr(uber_payment, attr, value)
#                         uber_payment.save()
#
#                 success_count += 1  # Увеличиваем счетчик успешных операций
#
#             except Exception as e:
#                 logger.error(f"Ошибка при обработке строки: {e}")
#                 fail_count += 1  # Увеличиваем счетчик неудачных операций
#                 continue
#
#     except Exception as e:
#         logger.error(f"Общая ошибка при импорте данных: {e}")
#         return f"Не удалось импортировать данные: {e}"
#
#     # Возврат сообщения о результате
#     result_message = f"Импорт завершен. Успешно импортировано {success_count} записей. Ошибок импорта {fail_count}."
#     logger.info(result_message)
#     return result_message


#############################################################################################################################


# def uber_import(request):
#     # Возвращает index.html шаблон в ответ на запрос
#     return render(request, 'uber_import.html')
#
#
# def import_uber_csv(request):
#     # Создаем логгер с именем 'uber_logger', который был определен в настройках
#     logger = logging.getLogger('uber_import.log')
#
#         # Используйте logger для записи логов
#     logger.info('Начало импорта данных Uber')
#     # logger.error('Это сообщение об ошибке')
#
#         # Счетчики
#     success_count = 0
#     fail_count = 0
#     if request.method == 'POST':
#         form = UberPaymentForm(request.POST, request.FILES)
#         try:
#             if form.is_valid():
#                 uber_csv_file = request.FILES['uber_csv'].read().decode('utf-8-sig').splitlines()
#                 csv_reader = csv.DictReader(uber_csv_file, delimiter=',')
#
#                 week_number = form.cleaned_data['week_number']
#                 week_start = form.cleaned_data['week_start']
#                 week_end = form.cleaned_data['week_end']
#
#                 for row in csv_reader:
#                     try:
#                         first_name = row['Meno vodiča']
#                         last_name = row['Priezvisko vodiča']
#
#                         driver, created = Driver.objects.get_or_create(
#                             first_name=first_name, last_name=last_name)
#
#                         uber_payment_data = {
#                             'total_earnings': Decimal(row['Celkové zárobky'].replace(',', '.')),
#                             'cash_collected': Decimal(row['Vyplatenia : Zozbieraná hotovosť'].replace(',', '.')),
#                         }
#
#                         with transaction.atomic():
#                             uber_payment, created = UberPayment.objects.get_or_create(
#                                 driver=driver,
#                                 week_start=week_start,
#                                 week_end=week_end,
#                                 week_number=week_number,
#                                 defaults={uber_payment_data}
#                             )
#
#                             if not created:
#                                 logger.info(f"Обновление существующей записи: {driver} за период {week_start} - {week_end} - {week_number}")
#                                 for attr, value in uber_payment_data.items():
#                                     setattr(uber_payment, attr, value)
#                                 uber_payment.save()
#
#                         success_count += 1  # Увеличиваем счетчик успешных операций
#                     except Exception as e:
#                         logger.error(f"Ошибка при обработке строки: {e}")
#                         fail_count += 1  # Увеличиваем счетчик неудачных операций
#                         continue
#
#         except Exception as e:
#             logger.error(f"Общая ошибка при импорте данных: {e}")
#             return f"Не удалось импортировать данные: {e}"
#
#     # Возврат сообщения о результате
#     result_message = f"Импорт завершен. Успешно импортировано {success_count} записей. Ошибок импорта {fail_count}."
#     logger.info(result_message)
#     return HttpResponse(result_message)

 ##################################################################################################################################
# @require_http_methods(["POST"])
# def import_uber_payments_view(request):
#     # Создаем экземпляр формы с данными POST и файлами
#     form = UberPaymentForm(request.POST, request.FILES)
#
#     # Проверяем, что форма заполнена корректно
#     if form.is_valid():
#         # Получаем файл из формы. Используем метод .get() на словаре,
#         # чтобы избежать ошибок, если 'uber_csv' не существует в request.FILES
#         csv_file_path = request.FILES.get('uber_csv')
#
#         # Проверяем, что файл действительно был загружен
#         if csv_file_path:
#             # Получаем остальные данные из формы
#             week_number = form.cleaned_data['week_number']
#             week_start = form.cleaned_data['week_start']
#             week_end = form.cleaned_data['week_end']
#
#
#             # Передаем файл и данные в функцию обработки CSV
#             result_message = import_uber_payments(csv_file_path, week_number, week_start, week_end)
#
#             # Возвращаем результат обработки клиенту
#             return HttpResponse(result_message)
#         else:
#             # Возвращаем ошибку, если файл не был загружен
#             return JsonResponse({'error': 'Файл не был загружен.'}, status=400)
#     else:
#         # Возвращаем ошибку, если данные формы некорректны
#         return JsonResponse({'error': 'Неверные данные формы.'}, status=400)
#
#
# def import_uber_payments(csv_file_path, week_start, week_end, week_number):
#     # Создаем логгер с именем 'uber_logger', который был определен в настройках
#     logger = logging.getLogger('uber_import.log')
#
#     # Используйте logger для записи логов
#     logger.info('Начало импорта данных Uber')
#
#     # Счетчики
#     success_count = 0
#     fail_count = 0
#
#     # Преобразование введенных дат в объекты datetime.date
#     # try:
#     #     week_start = datetime.strptime(week_start_date, '%d-%m-%Y').date()
#     #     week_end = datetime.strptime(week_end_date, '%d-%m-%Y').date()
#     # except ValueError as e:
#     #     logger.error(f"Ошибка в формате даты: {e}")
#     #     return "Ошибка в формате даты"
#
#     try:
#         with open(csv_file_path, encoding='utf-8') as csv_file:
#             reader = csv.DictReader(csv_file)
#             for row in reader:
#                 try:
#                     first_name = row['Meno vodiča']
#                     last_name = row['Priezvisko vodiča']
#
#                     driver, created = Driver.objects.get_or_create(
#                         first_name=first_name, last_name=last_name
#                     )
#
#                     uber_payment_data = {
#                         'driver': driver,
#                         'week_start': week_start,
#                         'week_end': week_end,
#                         'week_number': week_number,  # Добавляем номер недели
#                         # 'driver_uuid': row['UID vodiča'],
#                         'total_earnings': Decimal(row['Celkové zárobky'].replace(',', '.')),
#                         # 'net_fare_earnings': Decimal(row['Celkové zárobky : Čisté cestovné'].replace(',', '.')),
#                         # 'refunds_and_expenses': Decimal(row['Vrátenia peňazi a výdavky'].replace(',', '.')),
#                         # 'payouts': Decimal(row['Výplatenia'].replace(',', '.')),
#                         # 'payouts_to_bank_account': Decimal(row['Vyplatenia : Prevedené na bankový účet'].replace(',', '.')),
#                         'cash_collected': Decimal(row['Vyplatenia : Zozbieraná hotovosť'].replace(',', '.')),
#                         # 'tips': Decimal(row['Celkové zárobky:Prepitné'].replace(',', '.')),
#                         # 'promo_actions': Decimal(row['Celkové zárobky:Promo akcie'].replace(',', '.')),
#                         # 'toll_refunds': Decimal(row['Vrátenia peňazí a výdavky:Vrátenia peňazí:Mýto'].replace(',', '.')),
#
#                         # Добавление и преобразование остальных полей...
#                     }
#
#                     with transaction.atomic():
#                         uber_payment, created = UberPayment.objects.get_or_create(
#                             driver=driver,
#                             week_start=week_start,
#                             defaults=uber_payment_data
#                         )
#                         if not created:
#                             logger.info(f"Обновление существующей записи: {driver} за период {week_start} - {week_end}")
#                             for attr, value in uber_payment_data.items():
#                                 setattr(uber_payment, attr, value)
#                             uber_payment.save()
#
#                     success_count += 1  # Увеличиваем счетчик успешных операций
#
#                 except Exception as e:
#                     logger.error(f"Ошибка при обработке строки: {e}")
#                     fail_count += 1  # Увеличиваем счетчик неудачных операций
#                     continue
#
#     except Exception as e:
#         logger.error(f"Общая ошибка при импорте данных: {e}")
#         return f"Не удалось импортировать данные: {e}"
#
#     # Возврат сообщения о результате
#     result_message = f"Импорт завершен. Успешно импортировано {success_count} записей. Ошибок импорта {fail_count}."
#     logger.info(result_message)
#     return result_message

#######################################################################################################################################
def calculate_bolt_payout(driver_id):
    # Получаем данные водителя и выплат за интересующий период
    driver = Driver.objects.get(id=driver_id)
    payments = BoltPayment.objects.filter(driver=driver)

    # Расчет оборота водителя
    driver_turnover = sum(
        payment.gross_earnings - payment.bolt_commission + payment.bonus +
        payment.tips + payment.compensations + payment.cancellation_fee +
        payment.additional_charges - payment.refunds for payment in payments
    )

    # Вычет комиссии
    commission = driver_turnover * driver.park_commissions_bolt  # 13% комиссии!!!!!!!!!!!!!!!!!!!!!!!!!

    # Сумма наличных, полученных водителем
    cash_received = sum(payment.cash_collected for payment in payments)

    # Финальная выплата водителю без учета аренды автомобиля
    final_payout_bolt = driver_turnover - commission - cash_received

    return final_payout_bolt


def calculate_uber_payout(driver_id):
    # Получаем данные водителя и выплат за интересующий период
    driver = Driver.objects.get(id=driver_id)
    uber_payments = UberPayment.objects.filter(driver=driver)

    # Переменная для хранения итоговой выплаты
    final_payout_uber = 0

    # Расчет выплаты для каждой записи об оплате
    for payment in uber_payments:
        # Расчет заработка с вычетом комиссии Uber
        earnings_after_commission = payment.total_earnings * driver.park_commission_uber  # Вычет 11% комиссии!

        # Вычеты наличных
        earnings_after_deductions = earnings_after_commission - payment.cash_collected

        # Добавление бонусов
        earnings_after_deductions += payment.manual_bonus

        # Обновление итоговой выплаты
        final_payout_uber += earnings_after_deductions

    return final_payout_uber


def calculate_total_payout(driver_id):
    driver = Driver.objects.get(id=driver_id)

    # Расчет итоговых выплат от Bolt и Uber
    bolt_total = calculate_bolt_payout(driver_id)
    uber_total = calculate_uber_payout(driver_id)

    # Расчет общей аренды автомобиля
    # Предполагаем, что водитель арендует один и тот же автомобиль для обоих сервисов
    vehicle_rental = sum(payment.vehicle.rental_price for payment in driver.bolt_payments.all() | driver.uber_payments.all())

    # Итоговая выплата водителю от Bolt и Uber с однократным вычетом аренды автомобиля
    total_payout = (bolt_total + uber_total) - vehicle_rental

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



