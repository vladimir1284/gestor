from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest


@login_required
def list_roles(request: HttpRequest):
    roles = Group.objects.all()
    for r in roles:
        r.users_count = r.user_set.count()

    context = {
        "roles": roles,
    }
    return render(request, "rbac/list-roles.html", context)
