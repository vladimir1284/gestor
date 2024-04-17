from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest
from rbac.forms.passwords import SetUserPassForm
from rbac.forms.user_form import UserForm
from rbac.tools.get_role_perms import get_role_perms_all
from rbac.tools.get_roles_json import get_roles_json


@login_required
def user_create(request: HttpRequest):
    if request.method == "POST":
        form = UserForm(request.POST)
        pwf = SetUserPassForm(None, request.POST)
        if pwf.is_valid():
            if form.is_valid():
                user = form.save()

                pwf.user = user
                pwf.save()

                perms = get_role_perms_all(form.cleaned_data)
                user.user_permissions.set(perms)

                user.save()

                return redirect("rbac-list-users")
    else:
        form = UserForm()
        pwf = SetUserPassForm(None)

    context = {
        "form": form,
        "pwf": pwf,
        "user_instance": None,
        "title": "New user",
        "roles": get_roles_json(),
    }
    return render(request, "rbac/user_form.html", context)


@login_required
def user_update(request: HttpRequest, id=None):
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            perms = get_role_perms_all(form.cleaned_data)
            user.user_permissions.set(perms)
            user.save()
            return redirect("rbac-list-users")
    else:
        form = UserForm(instance=user)

    context = {
        "form": form,
        "pwf": None,
        "user_instance": user,
        "title": "Editing user",
        "roles": get_roles_json(),
    }
    return render(request, "rbac/user_form.html", context)
