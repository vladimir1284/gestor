from django.contrib.auth.models import Permission

from rbac.tools.urls_match import url_match


def get_url_perm(url: str) -> Permission | None:
    for up in Permission.objects.filter(
        content_type__model="rbac",
        content_type__app_label="urls",
    ):
        if url_match(url, str(up.codename)):
            return up
    return None
