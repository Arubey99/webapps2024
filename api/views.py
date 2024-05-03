from django.http import JsonResponse
from django.views import View

class CurrencyConverterView(View):
    exchange_rates = {
        'USD': {
            'EUR': 0.85,
            'GBP': 0.75,
            "USD": 1.0,
        },
        'EUR': {
            'USD': 1.18,
            'GBP': 0.88,
            "EUR": 1.0,
        },
        'GBP': {
            'USD': 1.34,
            'EUR': 1.14,
            "GBP": 1.0,
        }
    }

    def get(self, request, base_currency, target_currency, amount):
        base_currency = base_currency.upper()
        target_currency = target_currency.upper()

        try:
            amount = float(amount)
        except ValueError:
            return JsonResponse({'error': 'Invalid amount.'}, status=400)

        if base_currency not in self.exchange_rates or target_currency not in self.exchange_rates[base_currency]:
            return JsonResponse({'error': 'Invalid base or target currency.'}, status=400)

        converted_amount = amount * self.exchange_rates[base_currency][target_currency]
        return JsonResponse({'converted_amount': converted_amount})
