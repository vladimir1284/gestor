from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest
from rbac.forms.role_form import RoleForm
from rbac.tools.get_role_perms import get_role_perms


@login_required
def role_form(request: HttpRequest, id=None):
    group = Group.objects.filter(id=id).first()

    if request.method == "POST":
        form = RoleForm(request.POST, role=group)
        if form.is_valid():
            data = form.clean()
            if group is None:
                group = Group(name=data["name"])
                group.save()
            else:
                group.name = data["name"]

            group.user_set.set(data["users"])

            perms = []
            perms += get_role_perms(data, "menu")
            perms += get_role_perms(data, "urls")
            perms += get_role_perms(data, "dashboard_card")
            perms += get_role_perms(data, "extra_perm")

            group.permissions.set(perms)

            group.save()
            return redirect("rbac-list-roles")

    form = RoleForm(role=group)
    context = {
        "form": form,
        "role": group,
        "title": "New role" if group is None else "Editing role",
    }
    return render(request, "rbac/role_form.html", context)
