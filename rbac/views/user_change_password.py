from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeForm
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest


@login_required
def user_change_password(request: HttpRequest, id):
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("rbac-user-update", id)
    else:
        form = PasswordChangeForm(user)

    context = {
        "form": form,
        "user": user,
        "title": f"Change password for user {user.username}",
    }
    return render(request, "rbac/user_pass.html", context)
