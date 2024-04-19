from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest
from rbac.decorators.admin_required import admin_required


@login_required
@admin_required
def list_users(request: HttpRequest):
    users = User.objects.all()
    for u in users:
        u.roles_count = u.groups.count()

    context = {
        "users": users,
    }
    return render(request, "rbac/list-users.html", context)
