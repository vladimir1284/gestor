from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from rent.models.lease import Associated
from rent.models.lease import Contract
from rent.views.create_lessee_with_data import create_lessee
from rent.views.create_lessee_with_data import update_lessee


@login_required
def select_guarantor(request, contract_id: int):
    contract: Contract = get_object_or_404(Contract, id=contract_id)

    if request.method == "POST":
        gid = request.POST.get("id", None)
        if gid is not None:
            guar = Associated.objects.filter(id=gid).last()
            if guar is not None:
                return redirect("update-contract-guarantor", contract.id, guar.id)

    associates = Associated.objects.filter(type="client", active=True).order_by(
        "name", "alias"
    )
    context = {
        "associates": associates,
        "create": True,
        "createUrl": reverse("create-contract-guarantor", args=[contract_id]),
    }
    return render(request, "services/client_list.html", context)


@login_required
def update_guarantor(request, contract_id: int, guarantor_id: int):
    return update_lessee(
        request,
        guarantor_id,
        "use-contract-guarantor",
        [contract_id, "{lessee_id}"],
        update_data=False,
    )


@login_required
def create_guarantor(request, contract_id: int):
    return create_lessee(
        request,
        "use-contract-guarantor",
        [contract_id, "{lessee_id}"],
        use_client_url={
            "url": "update-contract-guarantor",
            "args": [
                contract_id,
                "{client_id}",
            ],
        },
        update_data=False,
    )


@login_required
def use_guarantor(request, contract_id: int, guarantor_id: int):
    contract: Contract = get_object_or_404(Contract, id=contract_id)
    guarantor: Associated = get_object_or_404(Associated, id=guarantor_id)

    contract.guarantor = guarantor
    contract.save()

    return redirect("detail-contract", contract_id)
