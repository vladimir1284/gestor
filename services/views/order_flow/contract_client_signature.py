import base64
import re
import tempfile

import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from services.forms import OrderSignatureForm
from services.models.order_signature import OrderSignature
from services.models.preorder import Preorder


def contact_create_handwriting(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        preorder_id = info["preorder"]
    except jwt.ExpiredSignatureError:
        context = {
            "title": "Error",
            "msg": "Expirated token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)
    except jwt.InvalidTokenError:
        context = {
            "title": "Error",
            "msg": "Invalid token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)

    preorder: Preorder = get_object_or_404(
        Preorder,
        id=preorder_id,
    )
    if preorder.completed is not None:
        return redirect("process-ended-page")

    if request.method == "POST":
        form = OrderSignatureForm(request.POST, request.FILES)
        if form.is_valid():
            handwriting: OrderSignature = form.save(commit=False)
            handwriting.associated = preorder.associated
            handwriting.position = "signature_order_client"

            # Save image
            datauri = str(form.instance.img)
            image_data = re.sub("^data:image/png;base64,", "", datauri)
            image_data = base64.b64decode(image_data)
            with tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, prefix="firma_"
            ) as output:
                output.write(image_data)
                output.flush()
                name = output.name.split("/")[-1]
                with open(output.name, "rb") as temp_file:
                    handwriting.img.save(name, temp_file, True)

            handwriting.save()
            preorder.signature = handwriting
            preorder.save()
            request.session["signature"] = handwriting.id
            return redirect("contact-view-conditions", token)
    else:
        form = OrderSignatureForm()

    context = {
        "position": "signature",
        "form": form,
        "preorder": preorder_id,
        "back": reverse("contact-view-conditions", args=[token]),
    }
    return render(request, "services/signature.html", context)


def contract_client_use_old_sign(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        preorder_id = info["preorder"]
    except jwt.ExpiredSignatureError:
        context = {
            "title": "Error",
            "msg": "Expirated token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_err.html", context)
    except jwt.InvalidTokenError:
        context = {
            "title": "Error",
            "msg": "Invalid token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_err.html", context)

    preorder: Preorder = get_object_or_404(Preorder, id=preorder_id)
    if preorder.completed is not None:
        return redirect("process-ended-page")

    old_sign = (
        OrderSignature.objects.filter(associated=preorder.associated).last()
        if preorder.associated is not None
        else None
    )
    preorder.signature = old_sign
    preorder.new_associated = False
    preorder.save()
    return redirect("contact-view-conditions", token)
