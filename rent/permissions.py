from django.shortcuts import render, redirect
from functools import wraps


def staff_required(view_func):
    """
    Decorator that checks if the user is a staff member and redirects to the login page if not.

    Args:
        view_func: The view function to be decorated.

    Returns:
        The decorated view function.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('staff_required')
        return view_func(request, *args, **kwargs)

    return wrapper


def staff_required_view(request):
    """
    View that displays a notification to the user that they do not have permission to access the requested resource.

    Args:
        request: The request object.

    Returns:
        A Django TemplateResponse object.
    """

    return render(
        request,
        'rent/staff_required.html',
        {
            'message': 'You do not have permission to modify this data!',
            'back_url': request.META['HTTP_REFERER'],
        },
    )
