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
