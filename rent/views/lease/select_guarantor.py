from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from rent.models.lease import Associated
from rent.models.lease import Contract


def select_guarantor(request: HttpRequest, id: int):
    contract: Contract = get_object_or_404(Contract, id=id)
    if request.method == "POST":
        gid = request.POST.get("id", None)
        if gid is not None:
            guar = Associated.objects.filter(id=gid).last()
            if guar is not None:
                contract.objects = guar
                contract.save()
                return redirect("detail-contract", contract.id)

    associates = Associated.objects.filter(type="client", active=True).order_by(
        "name", "alias"
    )
    context = {
        "associates": associates,
        "create": True,
    }
    return render(request, "services/client_list.html", context)
