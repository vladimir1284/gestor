from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.shortcuts import redirect

from rbac.decorators.admin_required import admin_required


@login_required
@admin_required
def delete_role(request: HttpRequest, id):
    Group.objects.filter(id=id).delete()
    return redirect("rbac-list-roles")
