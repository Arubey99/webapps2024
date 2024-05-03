from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from register.forms import RegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

def anonymous_required(function=None, redirect_url=None):
    """
    Decorator for views that checks that the user is not logged in, redirecting
    to the specified page if necessary.
    """
    if not redirect_url:
        redirect_url = '/home'

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


@csrf_protect
@anonymous_required(redirect_url='/home')
def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("login")
            # return HttpResponse("Homepage")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = RegisterForm()
    return render(request, "register/register.html", {"register_user": form})


@csrf_exempt
@anonymous_required(redirect_url='/home')
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                if user.is_staff:
                    return redirect('/staff/all_users/')  # Redirect to 'staff/all_transactions' if user is an admin
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "register/login.html", {"login_user": form})


def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")
