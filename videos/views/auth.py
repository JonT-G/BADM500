"""
Authentication views, register, login, and logout.
These views redirect away immediately if the user is already logged in.
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
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
            user = form.save()  # creates and saves the User in the database
            login(request, user)  # log the new user in right away
            messages.success(request, 'Account created! Welcome to BADM500.')
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


def logout_view(request):
    """Clear session and redirect to home."""
    logout(request)
    return redirect('index')
