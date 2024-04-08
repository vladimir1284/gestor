from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from services.models import ServicePicture
from services.tools.capture_picture import save_img
from services.views.category import get_object_or_404
from utils.models import Order


@login_required
def capture_service_picture(request: HttpRequest, order_id: int = 0):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        image = request.POST["img"]
        data, name, ext = save_img(image)
        pict = ServicePicture()
        pict.order = order
        pict.image.save(name, data, save=True)
        pict.save()
        return redirect("detail-service-order", order_id)

    ctx = {
        "title": "Take a picture",
        "back": reverse("detail-service-order", args=[order_id]),
    }
    return render(request, "services/picture/capture_picture.html", ctx)


def expense_capture_picture(request: HttpRequest, id: int, creating: bool = False):
    back = "create-expense" if creating else "update-expense"

    request.session["expenseCaptureImgBase64"] = None

    if request.method == "POST":
        image = request.POST["img"]
        request.session["expenseCaptureImgBase64"] = image
        return redirect(back, id)

    ctx = {
        "title": "Take a picture",
        "back": reverse(back, args=[id]),
    }
    return render(request, "services/picture/capture_picture.html", ctx)


@login_required
def update_expense_capture_picture(request: HttpRequest, expense_id: int):
    return expense_capture_picture(request, expense_id, False)


@login_required
def create_expense_capture_picture(request: HttpRequest, order_id: int):
    return expense_capture_picture(request, order_id, True)
