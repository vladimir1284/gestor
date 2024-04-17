from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest
from rbac.forms.passwords import ChangeUserPassForm
from rbac.forms.passwords import SetUserPassForm


@login_required
def user_change_password(request: HttpRequest, id):
    user = get_object_or_404(User, id=id)
    request.session["pass_saved"] = None
    if request.method == "POST":
        if request.user.has_perm("extra_perm.change_password"):
            form = SetUserPassForm(user, request.POST)
        else:
            form = ChangeUserPassForm(user, request.POST)
        if form.is_valid():
            form.save()
            request.session["pass_saved"] = True
            return redirect("rbac-user-update", id)
    else:
        if request.user.has_perm("extra_perm.change_password"):
            form = SetUserPassForm(user)
        else:
            form = ChangeUserPassForm(user)

    context = {
        "form": form,
        "user_instance": user,
        "title": f"Change password for user {user.username}",
    }
    return render(request, "rbac/user_pass.html", context)
