from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from services.tools.order import computeOrderAmount
from utils.models import Order


def _resolver():
    print("payment pending")
    orders_payment_pending = (
        Order.objects.filter(type="sell", status="payment_pending")
        .order_by("-created_date")
        .prefetch_related(
            "expense_set",
            "servicetransaction_set",
            "producttransaction_set",
            "producttransaction_set__product",
            "producttransaction_set__product__producttransaction_set",
            "producttransaction_set__product__producttransaction_set__order",
        )
    )

    for order in orders_payment_pending:
        computeOrderAmount(order)

    return {
        "payment_pending": orders_payment_pending,
    }


def PaymentPenddingCard():
    return DashboardCard(
        name="Ordenes pendientes por cobrar",
        template="dashboard/payment_pendding.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
