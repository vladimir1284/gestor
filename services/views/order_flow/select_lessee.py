from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from rent.models.lease import Contract


# Flow: client rent trailer
@login_required
def select_lessee(request):
    if request.method == "POST":
        client_id = request.POST.get("id")
        return redirect("select-service-lessee-trailer", id=client_id)

    contracts = Contract.objects.filter(stage="active").order_by(
        "lessee__name", "lessee__alias"
    )
    clients = []
    for contract in contracts:
        client = contract.lessee
        if client not in clients:
            clients.append(client)
    context = {
        "associates": clients,
        # "trailer_id": trailer_id,
        "create": False,
    }
    return render(request, "services/select_lessee.html", context)


@login_required
def select_lessee_trailer(request, id):
    if request.method == "POST":
        trailer_id = request.POST.get("id")
        contract = Contract.objects.get(
            stage="active", lessee__id=id, trailer__id=trailer_id
        )
        return redirect("view-contract-details", id=contract.id)

    contracts = Contract.objects.filter(stage="active", lessee__id=id)
    if contracts.count() == 1:
        return redirect("view-contract-details", id=contracts[0].id)

    trailers = []
    for contract in contracts:
        if contract.trailer not in trailers:
            trailers.append(contract.trailer)
    context = {
        "trailers": trailers,
    }
    return render(request, "services/select_trailer.html", context)
