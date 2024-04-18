from datetime import datetime
from datetime import timedelta

import jwt
import qrcode
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import reverse

from rent.tools.lessee_contact_sms import sendSMSLesseeContactURL
from services.views.order_flow.fast_orders import Preorder


@login_required
def generate_url(request, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)

    if request.method == "POST":
        return redirect("view-conditions", id)

    preorder.completed = None
    preorder.save()

    phone = (
        preorder.associated.phone_number if preorder.associated is not None else None
    )
    exp = datetime.utcnow() + timedelta(hours=2)
    context = {
        "preorder": preorder.id,
        "name": (preorder.associated.name if preorder.associated is not None else ""),
        "phone": str(phone) if phone is not None else "",
        "exp": exp,
    }

    token = jwt.encode(context, settings.SECRET_KEY, algorithm="HS256")

    url_base = "{}://{}".format(request.scheme, request.get_host())
    if preorder.new_associated:
        url = url_base + reverse("service-order-contact-form", args=[token])
    else:
        url = url_base + reverse("contact-view-conditions", args=[token])
    context["url"] = url

    if phone is not None:
        sendSMSLesseeContactURL(phone, url)

    factory = qrcode.image.svg.SvgPathImage
    factory.QR_PATH_STYLE["fill"] = "#455565"
    img = qrcode.make(
        url,
        image_factory=factory,
        box_size=20,
    )
    context["qr_url"] = img.to_string(encoding="unicode")

    context["preorder_state_url"] = reverse("view-preorder-state", args=[id])

    return render(request, "rent/client/lessee_url.html", context)
