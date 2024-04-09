from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from services.models.preorder import MAINTENANCE
from services.models.preorder import PARTS_SALE
from services.models.preorder import Preorder
from services.models.preorder import QUOTATION
from services.models.preorder_data import PreorderData
from users.models import Associated


@login_required
def select_client(request, id=None):
    if id is not None:
        preorder: Preorder = get_object_or_404(Preorder, id=id)
    else:
        preorder = Preorder(
            creating_order=True,
            concept=MAINTENANCE,
            using_signature=True,
        )
        preorder.save()
        id = preorder.id

    if request.method == "POST":
        client = get_object_or_404(Associated, id=request.POST.get("id"))
        if preorder.preorder_data is None:
            preorder_data = PreorderData.objects.filter(
                associated=client).last()
            if preorder_data is None:
                preorder_data = PreorderData.objects.create(
                    associated=client,
                )
            preorder.preorder_data = preorder_data
            preorder.save()
        else:
            preorder.preorder_data.associated = client
            preorder.preorder_data.save()
        # Redirect acording to the  corresponding flow
        if preorder.creating_order:
            if preorder.concept == QUOTATION or preorder.concept == PARTS_SALE:
                return redirect("fast-order-create", id)
            return redirect("view-conditions", id)
        elif preorder.order is not None:
            preorder.order.associated = client
            preorder.order.save()
            return redirect("detail-service-order", id=preorder.order.id)

    # add form dictionary to context
    associates = Associated.objects.filter(type="client", active=True).order_by(
        "name", "alias"
    )
    context = {
        "associates": associates,
        "skip": preorder.order is None,
        "create": "order",
    }
    return render(request, "services/client_list.html", context)
