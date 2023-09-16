import datetime
import os
from django.shortcuts import render
# from .models import Currency
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_API_EXCHANGE = 'https://api.exchangerate.host/timeseries'
CURRENCIES = [
    {'currency_code': "USD", 'currency_name': "US Dollar"},
    {'currency_code': "RUB", 'currency_name': "Ruble"},
    {'currency_code': "EUR", 'currency_name': "Euro"},
    {'currency_code': "ILS", 'currency_name': "Shekel"}
]


def base(request):
    # currencies = Currency.objects.all()
    # context = {'currencies': currencies}
    context = {'currencies': CURRENCIES}
    return render(request, 'base.html', context)


def get_currency_history(from_currency, to_currency, amount, start_date, end_date):
    payload = {
        'base': from_currency,
        'symbols': to_currency,
        'amount': amount,
        'start_date': start_date,
        'end_date': end_date
    }
    try:
        response = requests.get(URL_API_EXCHANGE, params=payload)
        data = response.json()
        currency_history = {}
        for date, rates in data['rates'].items():
            # Ensure date is a datetime.date object
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            if to_currency in rates:
                currency_history[date_obj] = rates[to_currency]
            else:
                # Handle the case where the rate is missing
                currency_history[date_obj] = None
        return currency_history
    except Exception as e:
        print(f'Error fetching data: {e}')
        return {}


def currency_converter_view(request, from_currency, amount, percent, to_currency, period):

    # Data collecting
    amount = float(amount)
    percent = float(percent)
    amount *= 1 + percent/100
    end_date = datetime.date.today()

    if period == '1m':
        start_date = end_date - datetime.timedelta(days=30)
    elif period == '1y':
        start_date = end_date - datetime.timedelta(days=365)
    elif period == '3y':
        start_date = end_date - datetime.timedelta(days=365*3)
    elif period == '5y':
        start_date = end_date - datetime.timedelta(days=365*5)
    else:
        # default 1 month
        start_date = end_date - datetime.timedelta(days=30)

    # Get data for each year in the selected period (API allows just 1 year query)
    rate_dates = []
    rate_values = []
    while start_date <= end_date:
        year_end_date = start_date + datetime.timedelta(days=365)
        if year_end_date > end_date:
            year_end_date = end_date

        year_currency_history = get_currency_history(
            from_currency, to_currency, amount, start_date, year_end_date)
        for date, rate in year_currency_history.items():
            parsed_date = date.strftime("%Y-%m-%d")  # Convert date to string
            rate_dates.append(parsed_date)
            rate_values.append(rate)

        start_date = year_end_date + datetime.timedelta(days=1)

    # currencies = Currency.objects.all()
    return render(request, 'currency_converter.html',
                  {'amount': amount,
                   'percent': percent,
                   'from_currency': from_currency,
                   'to_currency': to_currency,
                   #    'currencies': currencies,
                   'currencies': CURRENCIES,
                   'period': period,
                   'rate_dates': rate_dates, 'rate_values': rate_values})
