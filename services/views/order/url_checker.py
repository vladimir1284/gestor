from django.http import HttpRequest
from django.shortcuts import redirect


def url_list_order_checker(request: HttpRequest):
    if "order_back" in request.session:
        back = request.session["order_back"]
    else:
        back = None

    if back is None or back == "order":
        return redirect("list-service-order-direct")

    return redirect("storage-view", back)
