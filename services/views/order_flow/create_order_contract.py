from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rent.forms.lessee_contact import LesseeContactForm
from services.models.preorder import PARTS_SALE
from services.models.preorder import QUOTATION
from services.views.order_flow.fast_orders import Preorder
from users.models import Associated
from users.views import addStateCity


def on_exists(args: list, client: Associated):
    preorder: Preorder | None = args[0] if len(args) > 0 else None
    if preorder is None:
        preorder = Preorder(
            associated=client,
            new_associated=True,
            using_signature=True,
        )
    else:
        preorder.associated = client
        preorder.new_associated = True
        preorder.using_signature = False

    preorder.save()
    if preorder.concept == QUOTATION or preorder.concept == PARTS_SALE:
        return "fast-order-create", [preorder.id]
    return "generate-service-order-contact-url", [preorder.id]


@login_required
def create_order_contact(request, id=None):
    preorder: Preorder | None = (
        get_object_or_404(Preorder, id=id) if id is not None else None
    )

    if request.method == "POST":
        form = LesseeContactForm(
            request.POST,
            request.FILES,
            use_client_url={
                "url": "",
                "args": [preorder],
                "on_exists": on_exists,
            },
        )
        if form.is_valid():
            associated = form.save()

            if preorder is None:
                preorder = Preorder(
                    associated=associated,
                    new_associated=True,
                    using_signature=True,
                )
            else:
                preorder.associated = associated
                preorder.new_associated = True
                preorder.using_signature = False

            preorder.save()
            if preorder.concept == QUOTATION or preorder.concept == PARTS_SALE:
                return redirect("fast-order-create", preorder.id)
            return redirect("generate-service-order-contact-url", preorder.id)
    else:
        form = LesseeContactForm()

    title = _("Create client")

    context = {
        "form": form,
        "title": title,
    }
    addStateCity(context)
    return render(request, "users/lessee_contact_create.html", context)
