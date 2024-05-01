from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .order import getOrderContext
from .sms import twilioSendSMS
from inventory.models import ProductTransaction
from services.forms import PaymentCategoryCreateForm
from services.forms import PaymentCreateForm
from services.forms.towit_payment_form import TowitPaymentForm
from services.models import DebtStatus
from services.models import Order
from services.models import Payment
from services.models import PaymentCategory
from services.models import PendingPayment
from services.tools.transaction import handle_transaction
from users.models import Associated

# -------------------- Payment -------------------------


@login_required
def create_payment_category(request):
    form = PaymentCategoryCreateForm()
    if request.method == "POST":
        form = PaymentCategoryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("list-payment-category")
    context = {"form": form, "title": _("Create payment category")}
    return render(request, "services/payment_category_create.html", context)


@login_required
def update_payment_category(request, id):
    category = get_object_or_404(PaymentCategory, id=id)
    form = PaymentCategoryCreateForm(instance=category)
    if request.method == "POST":
        form = PaymentCategoryCreateForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect("list-payment-category")
    context = {"form": form, "title": _("Update payment category")}
    return render(request, "services/payment_category_create.html", context)


@login_required
def list_payment_category(request):
    # fetch the object related to passed id
    categories = PaymentCategory.objects.all()
    context = {"object_list": categories}
    return render(request, "services/payment_category_list.html", context)


@login_required
def delete_payment_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(PaymentCategory, id=id)
    category.delete()
    return redirect("list-payment-category")


@login_required
def pay_debt(request, client_id):
    categories = PaymentCategory.objects.all().exclude(name="debt")

    # Create a form for each category
    forms = []
    for category in categories:
        initial = {"category": category}
        forms.append(
            PaymentCreateForm(
                request.POST or None,
                prefix=category.name,
                initial=initial,
                auto_id=category.name + "_%s",
            )
        )

    client = get_object_or_404(Associated, id=client_id)

    if request.method == "POST":
        for form in forms:
            if form.is_valid():
                if form.cleaned_data["amount"] > 0:
                    # Check for double requests
                    if client.debt > 0:
                        payment = PendingPayment.objects.create(
                            client=client,
                            created_by=request.user,
                            amount=form.cleaned_data["amount"],
                            category=form.category,
                        )
                        # Discount debt
                        client.debt -= payment.amount
                        debt_status = DebtStatus.objects.get(client=client)
                        if client.debt == 0:
                            # Delete debt status data
                            debt_status.delete()
                        elif debt_status.weeks > 0:
                            debt_status.weeks -= 1
                            debt_status.save()

        client.save()
        return redirect("list-debtor")

    context = {"forms": forms, "client": client, "title": _("Pay debt ")}
    return render(request, "services/pending_payment.html", context)


@login_required
def update_debt_status(request, client_id, status):
    debt_status = get_object_or_404(DebtStatus, client__id=client_id)
    if status == "cleared":
        client = get_object_or_404(Associated, id=client_id)
        client.debt = 0
        client.save()
        debt_status.delete()
    else:
        debt_status.status = status
        debt_status.save()
    return redirect("list-debtor")


@login_required
def delete_payment(request, id, order_id):
    # fetch the object related to passed id
    payment = get_object_or_404(Payment, id=id)
    payment.delete()
    return redirect("detail-order", order_id)
