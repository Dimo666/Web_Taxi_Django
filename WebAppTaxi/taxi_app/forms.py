from django import forms


class BoltPaymentForm(forms.Form):
    bolt_csv_file = forms.FileField()
    week_number = forms.IntegerField(label='Введите номер недели')
    week_start = forms.DateField(label='Введите дату начала недели')
    week_end = forms.DateField(label='Введите дату конца недели')


class UberPaymentForm(forms.Form):
    uber_csv_file = forms.FileField()
    week_number = forms.IntegerField(label='Введите номер недели')
    week_start = forms.DateField(label='Введите дату начала недели')
    week_end = forms.DateField(label='Введите дату конца недели')
