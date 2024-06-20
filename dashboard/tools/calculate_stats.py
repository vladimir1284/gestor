from costs.models import Cost
from gestor.views.reports import computeReport
from rent.models.lease import LeaseDeposit
from rent.models.lease import SecurityDepositDevolution
from services.models import PendingPayment
from utils.models import Order


def calculate_stats(
    stats,
    start_date,
    end_date,
):
    """
    The "calculate_stats" function calculates various statistics based on the
    given parameters: "stats" (an object that stores the calculated stats),
    "start_date" (the start date for the data range), and "end_date" (the end
    date for the data range).
    The function first retrieves a list of completed sell orders within the
    specified date range, excluding any associated with a membership or company
    membership. It then fetches the costs and pending payments within the same
    date range.
    The function calls the "computeReport" function to compute the report based
    on the retrieved data. The computed values are then assigned to the
    corresponding attributes of the "stats" object.
    The function also calculates membership-related statistics by filtering the
    orders based on company membership. The computed values are again assigned
    to the relevant attributes of the "stats" object.
    Finally, the "stats" object is saved in the database.
    """

    orders = (
        Order.objects.filter(
            status="complete",
            type="sell",
            terminated_date__gt=start_date,
            terminated_date__lte=end_date,
        )
        .order_by("-terminated_date")
        .exclude(associated__membership=True)
        .exclude(company__membership=True, associated=None)
        .prefetch_related(
            "service_payment",
            "service_payment__category",
        )
        .prefetch_related("servicetransaction_set")
        .prefetch_related("expense_set")
        .prefetch_related(
            "producttransaction_set",
            "producttransaction_set__unit",
            "producttransaction_set__product",
            "producttransaction_set__product__unit",
            "producttransaction_set__product__producttransaction_set",
            "producttransaction_set__product__producttransaction_set__order",
        )
    )

    costs = (
        Cost.objects.filter(date__range=(start_date, end_date))
        .order_by("-date")
        .select_related("category")
    )

    pending_payments = (
        PendingPayment.objects.filter(
            created_date__gt=start_date, created_date__lte=end_date
        )
        .order_by("-created_date")
        .select_related("category")
    )

    context = computeReport(orders, costs, pending_payments)

    stats.completed_orders = len(orders)
    stats.gross_income = context["total"]["gross"]
    stats.profit_before_costs = context["total"]["net"]
    stats.labor_income = context["orders"].labor
    stats.discount = context["total"]["discount"]
    stats.third_party = context["total"]["third_party"]
    stats.supplies = context["total"]["consumable"]
    stats.costs = context["costs"].total
    stats.parts_cost = context["parts_cost"]
    stats.parts_price = context["parts_price"]
    stats.payment_amount = context["payment_total"]
    stats.transactions = context["payment_transactions"]
    stats.debt_paid = context["debt_paid"]

    stats.debt_created = 0
    for cat in context["payment_cats"]:
        if cat.name == "debt":
            stats.debt_created = cat.amount
            break

    # Membership stats
    orders = (
        Order.objects.filter(
            status="complete",
            type="sell",
            terminated_date__gt=start_date,
            terminated_date__lte=end_date,
        )
        .order_by("-terminated_date")
        .exclude(company__membership=False)
        .exclude(company=None)
        .prefetch_related(
            "service_payment",
            "service_payment__category",
        )
        .prefetch_related("servicetransaction_set")
        .prefetch_related("expense_set")
        .prefetch_related(
            "producttransaction_set",
            "producttransaction_set__unit",
            "producttransaction_set__product",
            "producttransaction_set__product__unit",
            "producttransaction_set__product__producttransaction_set",
            "producttransaction_set__product__producttransaction_set__order",
        )
    )

    context = computeReport(orders, costs, pending_payments)

    stats.membership_orders = len(context["orders"])
    stats.membership_amount = context["total"]["net"]

    total_security_payments = 0
    total_returned_security_payments = 0

    security_payments = LeaseDeposit.objects.filter(
        date__gt=start_date, date__lte=end_date
    ).order_by("-date")

    returned_security_payments = SecurityDepositDevolution.objects.filter(
        returned_date__gt=start_date, returned_date__lte=end_date
    ).order_by("-returned_date")

    for payment in security_payments:
        total_security_payments += payment.amount

    for payment in returned_security_payments:
        total_returned_security_payments += payment.amount

    stats.security_payments = total_security_payments
    stats.returned_security_payments = total_returned_security_payments

    stats.save()
