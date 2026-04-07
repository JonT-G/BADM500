"""
Authentication views, register and login.
These views redirect away immediately if the user is already logged in.
Logout is handled by Django's built-in LogoutView in urls.py.
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from ..forms import RegisterForm


def register_view(request):
    """
    Registration page, creates a new user account and logs them in immediately.
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request, user) 
            messages.success(request, f"New account created:{user.username}")
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """
    Login page.
    authenticate() checks the username and password against the database.
    If valid it returns the User object; if not, it returns None.
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', ''),
            password=request.POST.get('password', ''),
        )
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')
