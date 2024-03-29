from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.shortcuts import render

from menu.menu.menu_element import HttpRequest
from rbac.forms.role_form import RoleForm
from rbac.tools.set_role_menu_perms import set_role_menu_perms


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

            set_role_menu_perms(group, data)

            group.save()
            return redirect("rbac-list-roles")

    form = RoleForm(role=group)
    context = {
        "form": form,
        "role": group,
        "title": "New role" if group is None else "Editing role",
    }
    return render(request, "rbac/role_form.html", context)
