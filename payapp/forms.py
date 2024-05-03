from django import forms
from payapp import models
from payapp.models import MoneyRequest
from django.contrib.auth.models import User


class MoneyTransferForm(forms.ModelForm):
    enter_destination_username = forms.CharField(required=True)
    enter_amount_to_transfer = forms.DecimalField(required=True)

    class Meta:
        model = models.MoneyTransfer
        fields = ["enter_destination_username", "enter_amount_to_transfer"]

    def __init__(self, *args, **kwargs):
        super(MoneyTransferForm, self).__init__(*args, **kwargs)
        self.fields['enter_destination_username'].queryset = User.objects.filter(is_staff=False)


class MoneyRequestForm(forms.ModelForm):
    class Meta:
        model = MoneyRequest
        fields = ['receiver', 'receiver_amount']

    def __init__(self, *args, **kwargs):
        super(MoneyRequestForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].queryset = User.objects.filter(is_staff=False)