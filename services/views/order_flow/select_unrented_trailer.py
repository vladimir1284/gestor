from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from rent.models.lease import Contract
from rent.models.vehicle import Trailer
from services.models.preorder import Preorder
from users.models import Company


@login_required
def select_unrented_trailer(request):
    if request.method == "POST":
        trailer_id = request.POST.get("id")
        trailer = get_object_or_404(Trailer, id=trailer_id)
        towit, created = Company.objects.get_or_create(
            name="Towithouston",
            defaults={"name": "Towithouston"},
        )
        preorder = Preorder(
            company=towit,
            trailer=trailer,
        )
        preorder.save()
        return redirect("create-service-order", preorder.id)

    contracts = Contract.objects.select_related(
        "trailer",
    ).exclude(stage="ended")
    rented_trailers_ids = [c.trailer.id for c in contracts]

    # unrented_trailers = []
    unrented_trailers = Trailer.objects.filter(active=True).exclude(
        id__in=rented_trailers_ids
    )
    # for trailer in trailers:
    #     # Contracts
    #     has_contract = (
    #         Contract.objects.filter(trailer=trailer).exclude(
    #             stage="ended").exists()
    #     )
    #     if not has_contract:
    #         unrented_trailers.append(trailer)

    context = {
        "trailers": unrented_trailers,
    }
    return render(request, "services/select_trailer.html", context)
