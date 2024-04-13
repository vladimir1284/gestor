from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import SetPasswordForm
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest
from rbac.forms.user_form import UserForm


@login_required
def user_create(request: HttpRequest):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            pwf = SetPasswordForm(user, request.POST)
            if pwf.is_valid():
                user = pwf.save(commit=False)
                user.save()
                return redirect("rbac-list-users")
        pwf = SetPasswordForm(None, request.POST)
    else:
        form = UserForm()
        pwf = SetPasswordForm(None)

    context = {
        "form": form,
        "pwf": pwf,
        "user_instance": None,
        "title": "New user",
    }
    return render(request, "rbac/user_form.html", context)


@login_required
def user_update(request: HttpRequest, id=None):
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("rbac-list-users")
    else:
        form = UserForm(instance=user)

    context = {
        "form": form,
        "pwf": None,
        "user_instance": user,
        "title": "Editing user",
    }
    return render(request, "rbac/user_form.html", context)
