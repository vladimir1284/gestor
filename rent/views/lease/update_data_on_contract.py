from django.http import HttpRequest
from django.shortcuts import redirect, render

from rent.forms.lease import LesseeDataForm
from rent.models.lease import Contract, LesseeData
from rent.views.calendar import get_object_or_404
from users.forms import AssociatedCreateForm
from users.models import Associated


def update_data_on_contract(request: HttpRequest, id: int):
    contract: Contract = get_object_or_404(Contract, id=id)
    associated: Associated = contract.lessee
    lesseeData: LesseeData = get_object_or_404(
        LesseeData,
        associated=associated,
    )

    if request.method == "POST":
        formLesseeData = LesseeDataForm(
            request.POST,
            request.FILES,
            instance=lesseeData,
        )
        formAssociated = AssociatedCreateForm(
            request.POST,
            request.FILES,
            instance=associated,
        )
        # Validate both forms...
        lesseeDataValid = formLesseeData.is_valid()
        associatedValid = formAssociated.is_valid()
        # if A and B -> if A is false do not evaluatie B
        # So we evaluate A and B before
        if lesseeDataValid and associatedValid:
            formLesseeData.save()
            formAssociated.save()
            return redirect("detail-contract", id)
    else:
        formLesseeData = LesseeDataForm(instance=lesseeData)
        formAssociated = AssociatedCreateForm(instance=associated)

    ctx = {
        "formLesseeData": formLesseeData,
        "formAssociated": formAssociated,
    }
    return render(
        request,
        "rent/contract/contract_lesseedata_associated_edit.html",
        ctx,
    )
