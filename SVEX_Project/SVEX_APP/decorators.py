from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from .models import User

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated and is a manager
        if request.user.is_authenticated and request.user.is_manager:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You must be a manager to access this page.")
            return redirect('new_login')  # Redirect to login page 

    return _wrapped_view


def client_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_client:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You must be a Client to access this page.")
            return redirect('new_login')  # Redirect to login page

    return _wrapped_view