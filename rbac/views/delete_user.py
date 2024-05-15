from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import redirect

from rbac.decorators.admin_required import admin_required


@login_required
@admin_required
def delete_user(request: HttpRequest, id):
    User.objects.filter(id=id).delete()
    return redirect("rbac-list-users")
