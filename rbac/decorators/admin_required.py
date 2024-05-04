from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def admin_required(func=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            user = request.user

            if user is None:
                return redirect_to_login(next="")

            if not user.is_superuser:
                request.session["403"] = True
                return redirect("dashboard")

            return func(request, *args, **kwargs)

        return _wrapper_view

    return decorator(func)
