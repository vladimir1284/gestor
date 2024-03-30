from django.urls import get_resolver

from menu.menu.menu_element import PermissionParam


def is_decorated(func):
    return hasattr(func, "__wrapped__")


def show_urls(urls=None, level=""):
    if urls is None:
        urls = get_resolver().url_patterns

    result_urls = []
    for url in urls:
        if hasattr(url, "url_patterns"):
            result_urls += show_urls(url.url_patterns, f"{level}{url.pattern}")
        else:
            view_function = url.callback
            if getattr(view_function, "view_class", None):
                # For class-based views
                view_function = view_function.view_class
            if getattr(view_function, "_decorated_view", None):
                # For function-based views
                view_function = view_function._decorated_view
            if is_decorated(view_function):
                result_urls.append(f"{level}{url.pattern}")

    return result_urls


def get_urls_perms():
    urls = show_urls()
    clean_urls = []
    for u in urls:
        if u == "erp/" or u.startswith("erp/admin/") or not u.startswith("erp/"):
            continue
        components: list[str] = u.split("/")
        cleaned = []
        for c in components:
            if c.startswith("<") and c.endswith(">"):
                cleaned.append("+")
            elif c != "":
                cleaned.append(c)
        url = "/".join(cleaned)
        if url not in clean_urls:
            clean_urls.append("/" + url)

    perms: list[PermissionParam] = []
    for u in clean_urls:
        perms.append(
            PermissionParam(
                app="urls",
                code=u,
                name=u.replace("+", "<PARAM>"),
            )
        )

    return perms
