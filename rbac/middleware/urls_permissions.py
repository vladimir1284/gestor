from django.contrib.auth.views import redirect_to_login

from menu.menu.menu_element import HttpRequest
from rbac.tools.get_url_perm import get_url_perm


class UrlsPermissions:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        url = request.get_full_path()
        perm = get_url_perm(url)

        if perm is not None:
            user = request.user
            if user is None or not user.has_perm(
                f"{perm.content_type.app_label}.{perm.codename}"
            ):
                return redirect_to_login(next=url)

        response = self.get_response(request)
        return response
