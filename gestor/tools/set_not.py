from django.http import HttpRequest


def set_not(request: HttpRequest, title: str, msg: str = "", icon="bxs-info-circle"):
    notify = {
        "title": title,
        "msg": msg,
        "icon": icon,
    }
    if "notify" not in request.session or not isinstance(
        request.session["notify"], list
    ):
        request.session["notify"] = [notify]
    else:
        request.session["notify"].append(notify)


def get_not(request: HttpRequest):
    if "notify" not in request.session or not isinstance(
        request.session["notify"], list
    ):
        return []
    nots = request.session["notify"]
    request.session["notify"] = []
    return {
        "notifications": nots,
    }
