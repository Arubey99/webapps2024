"""
URL configuration for webapps2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from api import views as api_views
from register import views as register_views
from payapp import views as transactions_views
from staff import views as staff_views

urlpatterns = [
    path('', register_views.login_user, name='login_home'),
    path('admin/', admin.site.urls),

    path("register/", register_views.register_user, name="register"),
    path("login/", register_views.login_user, name="login"),
    path("logout/", register_views.logout_user, name="logout"),

    path('home/', transactions_views.home, name="home"),
    path('moneytransfer/', transactions_views.money_transfer, name='money_transfer'),
    path('history/', transactions_views.view_transaction_history, name='transaction-history'),
    path('notification/', transactions_views.view_transaction_history, name='notification'),
    path('requests/', transactions_views.view_requests, name='requests'),
    path('request_money/', transactions_views.request_money, name='request_money'),
    # accept_reject_request
    path('accept_reject_request/<int:request_id>/<str:action>/', transactions_views.accept_reject_request, name='accept_reject_request'),

    path('api/conversion/<str:base_currency>/<str:target_currency>/<str:amount>/',api_views.CurrencyConverterView.as_view(), name='currency_converter'),

    # add the URLs for the AllUsersView and AllTransactionsView views
    path('staff/all_users/', staff_views.AllUsersView, name='all_users'),
    path('staff/all_transactions/', staff_views.AllTransactionsView, name='all_transactions'),
    path('staff/register_staff/', staff_views.register_staff, name='register_staff'),
]
