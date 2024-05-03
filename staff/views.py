from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from payapp.models import TransactionHistory, MoneyRequest, Money
from register.forms import RegisterForm
from django.contrib import messages

def is_staff(user):
    return user.is_staff

def get_user_money_and_currency(user):
    money_object = Money.objects.get(name=user)
    return money_object.money, money_object.currency


@login_required
@user_passes_test(is_staff)
def AllUsersView(request):
    users = User.objects.all()
    user_data = []
    for user in users:
        try:
            money_object = Money.objects.get(name=user)
            money = money_object.money
            currency = money_object.currency
        except Money.DoesNotExist:
            money = None
            currency = None
        user_info = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'money': money,
            'currency': currency,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined,  # add this line
            'last_login': user.last_login  # add this line
        }
        user_data.append(user_info)
    return render(request, 'staff/all_users.html', {'users': user_data})


@login_required
@user_passes_test(is_staff)
def AllTransactionsView(request):
    transactions = TransactionHistory.objects.all()
    for transaction in transactions:
        transaction.type = 'TransactionHistory'

    money_requests = MoneyRequest.objects.all()
    for money_request in money_requests:
        money_request.type = 'MoneyRequest'
        money_request.status = money_request.status  # add this line

    all_transactions = list(transactions) + list(money_requests)
    all_transactions = sorted(all_transactions, key=lambda x: x.timestamp, reverse=True)

    return render(request, 'staff/all_transactions.html', {'all_transactions': all_transactions})


@login_required
@user_passes_test(lambda user: user.is_staff)
def register_staff(request):
    form = RegisterForm()  # define form here
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')  # get password from POST data
        confirm_password = request.POST.get('confirm_password')  # get confirm_password from POST data
        if username and password and password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'A user with this username already exists.')
            else:
                user = User.objects.create_user(username=username, password=password)
                user.is_staff = True  # set is_staff to True
                user.save()
                return redirect('all_users')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'staff/register_staff.html', {'form': form})