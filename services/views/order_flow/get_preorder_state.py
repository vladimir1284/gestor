from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from services.views.order_flow.fast_orders import Preorder


@login_required()
def preorder_state(request, preorder_id):
    preorder = Preorder.objects.filter(id=preorder_id).first()
    return JsonResponse(
        {
            "ready": preorder.completed is False if preorder is not None else None,
        }
    )
