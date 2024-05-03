from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction, OperationalError
from django.db.models import Q

from . import models
from payapp.forms import MoneyTransferForm
from .models import Money, TransactionHistory
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MoneyRequest
from .forms import MoneyRequestForm

import requests


#@login_required()
#def home(request):
#    user_balance = models.Money.objects.get(name_id=request.user)
#    currency = models.Money.objects.get(name_id=request.user).currency
#    return render(request, 'app/home.html', {'user_balance': user_balance, 'currency': currency})

# Create your views here.
@login_required()
def money_transfer(request):
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST)

        if form.is_valid():
            src_username = request.user
            src_id = User.objects.get(username=src_username).id
            dst_username = form.cleaned_data["enter_destination_username"]

            #Check destination user is exists
            if not User.objects.filter(username=dst_username).exists():
                messages.error(request, "Destination user does not exist.")
                user_balance = round(Money.objects.get(name=request.user).money, 2)
                currency = Money.objects.get(name=request.user).currency
                return render(request, "transactions/moneytransfer.html", {"form": form, 'user_balance': user_balance, 'currency': currency})

            dst_id = User.objects.get(username=dst_username).id
            money_to_transfer = round(form.cleaned_data["enter_amount_to_transfer"], 2)

            # Get Currencies from usernames

            base_currency = models.Money.objects.get(name=src_id).currency
            target_currency = models.Money.objects.get(name=dst_id).currency

            # Make a GET request to the currency conversion API
            response = requests.get(f'http://localhost:8000/api/conversion/{base_currency}/{target_currency}/{money_to_transfer}/')

            # Check if the request was successful

            if str(src_username) == dst_username:
                messages.error(request, "You cannot send money to yourself.")
                user_balance = round(Money.objects.get(name=request.user).money, 2)
                currency = Money.objects.get(name=request.user).currency
                return render(request, "transactions/moneytransfer.html", {"form": form, 'user_balance': user_balance, 'currency': currency})

            if response.status_code == 200:
                # Get the converted amount from the response
                converted_amount = round(response.json()['converted_amount'], 2)
                print(converted_amount)

                src_money = models.Money.objects.select_related().get(name__username=src_username)
                dst_money = models.Money.objects.select_related().get(name__username=dst_username)

                try:
                    with transaction.atomic():
                        if src_money.money >= money_to_transfer:
                            src_money.money = round(src_money.money - Decimal(money_to_transfer), 2)
                            dst_money.money = round(dst_money.money + Decimal(converted_amount), 2)
                            src_money.save()
                            dst_money.save()
                            # Log the transaction
                            TransactionHistory.objects.create(
                                sender=User.objects.get(username=src_username),
                                receiver=User.objects.get(username=dst_username),
                                sender_amount=money_to_transfer,
                                receiver_amount=converted_amount,
                                sender_currency=base_currency,
                                receiver_currency=target_currency,
                            )
                            user_balance = round(Money.objects.get(name=request.user).money, 2)
                            currency = Money.objects.get(name=request.user).currency
                            return render(request, "transactions/money.html", {"src_money": src_money, "dst_money": dst_money, 'user_balance': user_balance, 'currency': currency, "send_money": money_to_transfer})

                        else:
                            messages.error(request, "Insufficient money to transfer.")
                        user_balance = round(Money.objects.get(name=request.user).money, 2)
                        currency = Money.objects.get(name=request.user).currency
                        return render(request, "transactions/moneytransfer.html", {"form": form, 'user_balance': user_balance, 'currency': currency})

                except OperationalError:
                    messages.info(request, f"Transfer operation is not possible now.")

            else:
                # If the request was not successful, return an error message
                messages.error(request, "Currency conversion failed.")
                user_balance = round(Money.objects.get(name=request.user).money, 2)
                currency = Money.objects.get(name=request.user).currency
                return render(request, "transactions/moneytransfer.html", {"form": form, 'user_balance': user_balance, 'currency': currency})

        user_balance = round(Money.objects.get(name=request.user).money, 2)
        currency = Money.objects.get(name=request.user).currency
        try:
            return render(request, "transactions/money.html", {"src_money": src_money, "dst_money": dst_money, 'user_balance': user_balance, 'currency': currency})
        except:
            return render(request, "transactions/moneytransfer.html", {"form": form, 'user_balance': user_balance, 'currency': currency})
    else:
        form = MoneyTransferForm()
    user_balance = round(Money.objects.get(name=request.user).money, 2)
    currency = Money.objects.get(name=request.user).currency
    return render(request, "transactions/moneytransfer.html", {"form": form, 'user_balance': user_balance, 'currency': currency})

@login_required
def view_transaction_history(request):
    sent_transactions = TransactionHistory.objects.filter(sender=request.user).order_by('-timestamp')
    received_transactions = TransactionHistory.objects.filter(receiver=request.user).order_by('-timestamp')

    # Get the money transfer requests
    sent_requests = MoneyRequest.objects.filter(sender=request.user).order_by('-timestamp')
    received_requests = MoneyRequest.objects.filter(receiver=request.user).order_by('-timestamp')

    user_balance = Money.objects.get(name=request.user).money
    user_balance = "{:.2f}".format(user_balance)  # format the balance to always show 2 decimal places
    currency = Money.objects.get(name=request.user).currency
    return render(request, 'transactions/transaction_history.html', {
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions,
        'sent_requests': sent_requests,
        'received_requests': received_requests,
        'user_balance': user_balance,
        'currency': currency
    })

@login_required
def request_money(request):
    if request.method == 'POST':
        form = MoneyRequestForm(request.POST)
        if form.is_valid():
            sender = request.user
            sender_currency = Money.objects.get(name=sender).currency
            receiver = form.cleaned_data['receiver']
            receiver_currency = Money.objects.get(name=receiver).currency
            reciver_amount = form.cleaned_data['receiver_amount']

            if sender == receiver:
                messages.error(request, "You cannot send a request to yourself.")
                return redirect('/requests')


            money_request = form.save(commit=False)
            money_request.sender = request.user
            print(sender_currency, receiver_currency)
            money_request.receiver_currency = receiver_currency

            # Make a GET request to the currency conversion API
            response = requests.get(f'http://localhost:8000/api/conversion/{sender_currency}/{receiver_currency}/{reciver_amount}/')

            if response.status_code == 200:
                converted_amount = response.json()['converted_amount']
                money_request.sender_amount = converted_amount
            else:
                messages.error(request, "Currency conversion failed.")
                return redirect('/requests')

            money_request.save()


    form = MoneyRequestForm()
    sent_requests = MoneyRequest.objects.filter(sender_id=request.user, status='P')
    received_requests = MoneyRequest.objects.filter(receiver_id=request.user, status='P')
    sender_id = sent_requests.values_list('sender_id')
    receiver_id = received_requests.values_list('receiver_id')
    user_balance = Money.objects.get(name=request.user).money
    currency = Money.objects.get(name=request.user).currency

    return render(request, 'transactions/requests.html', {'request_form': form, 'sent_requests': sent_requests, 'received_requests': received_requests, 'user_balance': user_balance, 'currency': currency})

@login_required
def view_requests(request):
    form = MoneyRequestForm()
    sent_requests = MoneyRequest.objects.filter(sender=request.user, status='P')
    received_requests = MoneyRequest.objects.filter(receiver=request.user, status='P')
    user_balance = Money.objects.get(name=request.user).money
    currency = Money.objects.get(name=request.user).currency

    return render(request, 'transactions/requests.html', {'request_form': form, 'sent_requests': sent_requests, 'received_requests': received_requests, 'user_balance': user_balance, 'currency': currency, })

@login_required
def accept_reject_request(request, request_id, action):
    money_request = MoneyRequest.objects.get(id=request_id, receiver=request.user)
    if action == 'accept':
        money_request.status = 'A'
        sender = money_request.sender
        receiver = money_request.receiver
        receiver_amount = Decimal(money_request.receiver_amount)  # convert to Decimal
        sender_amount = Decimal(money_request.sender_amount)  # convert to Decimal
        sender_balance = Money.objects.get(name=sender)
        receiver_balance = Money.objects.get(name=receiver)
        try:
            with transaction.atomic():
                print(receiver_balance)
                print(sender_balance)
                if receiver_balance.money >= sender_amount:
                    receiver_balance.money -= sender_amount
                    sender_balance.money += receiver_amount
                    receiver_balance.save()
                    sender_balance.save()
                    money_request.save()
                    return redirect('transaction-history')
                else:
                    messages.error(request, "Sender does not have enough money.")
                    return redirect('transaction-history')
        except Exception as e:
            messages.error(request, f"An error occurred during the transaction: {str(e)}")
            return redirect('transaction-history')
        else:
            messages.error(request, "Failed to convert currency.")
            return redirect('transaction-history')

    else:
        messages.error(request, f"You have rejected the request from {money_request.sender.username} for {money_request.receiver_amount}.")
        money_request.status = 'R'
        money_request.save()
        return redirect('requests')

    money_request.save()
    return redirect('transaction-history')


@login_required
def home(request):
    # Get the user's balance
    user_balance = Money.objects.get(name=request.user).money

    # Get the last 10 transactions involving the logged in user
    last_transactions = TransactionHistory.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')[:5]

    # Get the last 10 money requests involving the logged in user
    last_requests = MoneyRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')[:5]

    currency = Money.objects.get(name=request.user).currency
    return render(request, 'app/home.html', {
        'user_balance': user_balance,
        'last_transactions': last_transactions,
        'last_requests': last_requests,
        'currency': currency,
    })