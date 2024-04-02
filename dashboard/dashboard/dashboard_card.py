import inspect
from typing import Callable

from django.http import HttpRequest
from django.shortcuts import loader

from rbac.tools.permission_param import PermissionParam


class DashboardCard:
    def __init__(
        self,
        name: str,
        resolver: Callable,
        template: str,
        dj_perms: list[str] | None = None,
        self_perm: PermissionParam | None = None,
    ) -> None:
        self.name = name
        self.resolver = resolver
        self.template = template
        self.dj_perms = dj_perms
        if self_perm is not None:
            if self_perm.app == "":
                self_perm.app = "dashboard_card"
            if self_perm.name == "":
                self_perm.name = name
            if self_perm.code == "":
                self_perm.code = name.lower().replace(" ", "_")
        self.self_perm = self_perm

    def has_perm(self, request) -> bool:
        if self.self_perm is None and (
            self.dj_perms is None or len(self.dj_perms) == 0
        ):
            return True

        user = request.user

        sp = self.self_perm is None or user.has_perm(self.self_perm.get_perm)

        dp = self.dj_perms is None or len(self.dj_perms) == 0
        if self.dj_perms is not None:
            for p in self.dj_perms:
                if user.has_perm(p):
                    dp = True
                    break

        return sp and dp

    def render(self, request: HttpRequest) -> str:
        if not self.has_perm(request):
            return ""

        parameters = inspect.signature(self.resolver).parameters
        if "request" in parameters or "kwargs" in parameters:
            ctx = self.resolver(request)
        else:
            ctx = self.resolver()
        ctx["title"] = self.name
        html = loader.render_to_string(self.template, ctx, request)
        return html
