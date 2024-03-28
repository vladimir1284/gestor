from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest


@login_required
def list_roles(request: HttpRequest):
    roles = Group.objects.all()
    context = {
        "roles": roles,
    }
    return render(request, "rbac/list-roles.html", context)
