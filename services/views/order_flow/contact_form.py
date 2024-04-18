import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from rent.forms.lessee_contact import LesseeContactForm
from services.models.preorder import Preorder
from users.views import addStateCity


def lessee_form(request, token):
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

    preorder: Preorder = get_object_or_404(Preorder, id=preorder_id)
    if preorder.completed is not None:
        return redirect("process-ended-page")

    associated = preorder.associated

    if request.method == "POST":
        form = LesseeContactForm(
            request.POST,
            request.FILES,
            instance=associated,
        )
        if form.is_valid():
            form.save()
            return redirect("contact-view-conditions", token)

    form = LesseeContactForm(instance=associated)
    title = _("Complete form")

    context = {
        "form": form,
        "title": title,
    }
    addStateCity(context)
    return render(request, "users/lessee_form.html", context)
