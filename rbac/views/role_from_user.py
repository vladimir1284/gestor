from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import JsonResponse

from rbac.decorators.admin_required import admin_required
from rbac.tools.role_from_user import create_role_from_user


@login_required
@admin_required
def new_role_from_user(request: HttpRequest, user_id: int, role_name: str):
    ret = create_role_from_user(user_id, role_name)
    return JsonResponse(ret, status=200 if "role_id" in ret else 400)
