from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from services.forms import (
    ExpenseCreateForm,
)
from services.models import Expense
from services.models import Order
from services.tools.capture_picture import save_img
from users.models import (
    Associated,
)

# -------------------- Expense ----------------------------


@login_required
def create_expense(request, order_id):
    associated_id = request.session.get("associated_id")
    capUrl = reverse("create-expense-capture-picture", args=[order_id])
    initial = {}
    if associated_id is not None:
        initial = {"associated": associated_id}
        request.session["associated_id"] = None
    form = ExpenseCreateForm(initial=initial, capUrl=capUrl)
    if request.method == "POST":
        form = ExpenseCreateForm(request.POST, request.FILES, capUrl=capUrl)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.order = get_object_or_404(Order, id=order_id)
            if request.session["expenseCaptureImgBase64"]:
                data, name, ext = save_img(
                    request.session["expenseCaptureImgBase64"])
                expense.image.save(name, data, save=True)
                request.session["expenseCaptureImgBase64"] = None
            expense.save()
            return redirect("detail-service-order", order_id)
    context = {
        "form": form,
        "outsource": Associated.objects.filter(
            type="provider", active=True, outsource=True
        ).order_by("name", "alias"),
        "title": _("Add third party expense"),
    }
    return render(request, "services/expense_create.html", context)


@login_required
def update_expense(request, id):
    # fetch the object related to passed id
    expense = get_object_or_404(Expense, id=id)
    capUrl = reverse("update-expense-capture-picture", args=[id])
    associated_id = request.session.get("associated_id")
    if associated_id is not None:
        associated = get_object_or_404(Associated, id=associated_id)
        expense.associated = associated
        request.session["associated_id"] = None
    # pass the object as instance in form
    form = ExpenseCreateForm(instance=expense, capUrl=capUrl)

    if request.method == "POST":
        # pass the object as instance in form
        form = ExpenseCreateForm(
            request.POST, request.FILES, instance=expense, capUrl=capUrl
        )

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            exp = form.save()
            if request.session["expenseCaptureImgBase64"]:
                data, name, ext = save_img(
                    request.session["expenseCaptureImgBase64"])
                exp.image.save(name, data, save=True)
                exp.save()
                request.session["expenseCaptureImgBase64"] = None
            return redirect("detail-service-order", expense.order.id)

    # add form dictionary to context
    context = {
        "form": form,
        "outsource": Associated.objects.filter(
            type="provider", active=True, outsource=True
        ).order_by("name", "alias"),
        "expense": expense,
        "title": _("Update third party expense"),
    }

    return render(request, "services/expense_create.html", context)


@login_required
def delete_expense(request, id):
    # fetch the object related to passed id
    expense = get_object_or_404(Expense, id=id)
    expense.delete()
    return redirect("detail-service-order", expense.order.id)
