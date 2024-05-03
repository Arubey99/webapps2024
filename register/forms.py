from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from payapp.models import Money

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    currency_choices = [
        ('GBP', 'GB Pounds'),
        ('USD', 'US Dollars'),
        ('EUR', 'Euros'),
    ]
    currency = forms.ChoiceField(choices=currency_choices, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "currency", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()

        selected_currency = self.cleaned_data['currency']
        base_money = 1000  # Base money in GBP

        # Hardcoded exchange rates as of today
        exchange_rates = {
            'GBP': 1,
            'USD': 1.24,
            'EUR': 1.14
        }

        # Calculate converted money based on the selected currency
        converted_money = int(base_money * exchange_rates[selected_currency])

        Money.objects.create(
            name=user,
            money=converted_money,
            currency=selected_currency
        )

        return user
