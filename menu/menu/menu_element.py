from django.http import HttpRequest
from django.template import loader
from django.urls import reverse

from rbac.tools.permission_param import PermissionParam


class MenuItem:
    def __init__(
        self,
        name: str,
        icon: str | None = None,
        url: str | None = None,
        children: list | None = None,
        i18n: str | None = None,
        dj_perms: list[str] | None = None,
        exact_match: bool = False,
        extra_match: list[str] | None = None,
        self_perm: PermissionParam | None = None,
    ):
        self.name: str = name
        self.icon: str | None = icon
        self.url: str | None = url
        self.children: list[MenuItem] | None = children
        self.i18n: str = i18n if i18n is not None else name
        self.dj_perms: list[str] | None = dj_perms
        self.exact_match: bool = exact_match
        self.extra_match = extra_match
        self.matchs = None

        if self_perm is not None and self_perm.app == "":
            self_perm.app = "menu"

        self.self_perm = self_perm

    @property
    def header(self):
        return self.url is None and self.children is None

    @property
    def link(self):
        return self.url is not None and self.children is None

    @property
    def submenu(self):
        return self.url is None and self.children is not None

    @property
    def has_icon(self):
        return self.icon is not None

    def getMatchs(self, url: str | None, exctra_match: list[str] | None):
        matchs = []

        if url is not None:
            matchs.append(reverse(url))

        if exctra_match is not None:
            for u in exctra_match:
                matchs.append(reverse(u))

        return matchs

    def match(self, url: str) -> bool:
        if self.matchs is None:
            self.matchs = self.getMatchs(self.url, self.extra_match)

        if self.exact_match:
            for u in self.matchs:
                if url == u:
                    return True
        else:
            for u in self.matchs:
                if url.startswith(u):
                    return True
        return False

    def is_active(self, request: HttpRequest, recursive: bool = False) -> bool:
        path = request.get_full_path()
        if self.match(path):
            return True

        if recursive and self.children is not None:
            for c in self.children:
                if c.is_active(request, recursive):
                    return True

        return False

    def has_perms(self, request) -> bool:
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

    def should_render(self, request) -> bool:
        if not self.has_perms(request):
            return False

        if self.children is None or len(self.children) == 0:
            return True

        for c in self.children:
            if c.has_perms(request):
                return True

        return False

    def render(self, request):
        if not self.should_render(request):
            return ""

        content = loader.render_to_string(
            "menu/menu_item.html",
            {
                "MenuItem": self,
            },
            request,
        )
        return content

    def get_permission_list(self) -> list[PermissionParam]:
        perms: list[PermissionParam] = []
        if self.self_perm is not None:
            perms.append(self.self_perm)

        if self.children is not None:
            for c in self.children:
                cps = c.get_permission_list()
                perms += cps

        return perms
