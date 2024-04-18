from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from rent.forms.lessee_contact import LesseeContactForm
from services.views.order_flow.fast_orders import Preorder
from users.views import addStateCity


@login_required
def create_order_contact(request):
    if request.method == "POST":
        form = LesseeContactForm(request.POST, request.FILES)
        if form.is_valid():
            associated = form.save()
            preorder = Preorder.objects.create(
                associated=associated,
                new_associated=True,
                using_signature=True,
            )
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
