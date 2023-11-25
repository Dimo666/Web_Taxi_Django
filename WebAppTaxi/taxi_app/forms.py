from django import forms


class BoltPaymentForm(forms.Form):
    bolt_csv = forms.FileField()
    week_number = forms.IntegerField()
    week_start = forms.DateField()
    week_end = forms.DateField()


class UberPaymentForm(forms.Form):
    uber_csv_file = forms.FileField()
    week_number = forms.IntegerField(label='Введите номер недели')
    week_start = forms.DateField(label='Введите дату начала недели')
    week_end = forms.DateField(label='Введите дату конца недели')
