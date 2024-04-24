from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from services.models import Order
from services.models.preorder import PARTS_SALE
from services.models.preorder import Preorder
from services.models.preorder import QUOTATION


@login_required
def fast_order_create(request, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)
    order = Order(
        concept=preorder.concept,
        quotation=preorder.concept == QUOTATION,
        parts_sale=preorder.concept == PARTS_SALE,
        created_by=request.user,
        associated=preorder.associated,
        type="sell",
    )
    order.save()
    preorder.order = order
    preorder.save()
    return redirect("detail-service-order", id=order.id)


@login_required
def parts_sale(request):
    preorder = Preorder()
    preorder.concept = PARTS_SALE
    preorder.save()
    return redirect("select-service-client", preorder.id)


@login_required
def order_quotation(request):
    preorder = Preorder()
    preorder.concept = QUOTATION
    preorder.save()
    return redirect("select-service-client", preorder.id)
