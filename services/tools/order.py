from datetime import datetime, timedelta

import pytz
from services.models import Payment
from utils.models import Associated, Order


def getDebtOrders(debtor: Associated):
    orders = Order.objects.filter(
        associated=debtor, type="sell", status="complete"
    ).order_by("-terminated_date")
    pending_orders = []
    debt = debtor.debt
    for order in orders:
        debt_payment = Payment.objects.filter(
            order=order, category__name="debt"
        ).first()
        if debt_payment is not None:
            # Order with pending payment
            if debt > 0:
                order.debt = debt_payment.amount
                pending_orders.append(order)
                debt -= debt_payment.amount
            else:
                break
    return pending_orders


def getRepairDebt(client: Associated):
    try:
        oldest_debt = getDebtOrders(client)[-1]
        overdue = oldest_debt.terminated_date < (
            datetime.now(pytz.timezone("UTC")) - timedelta(days=14)
        )
        weekly_payment = client.oldest_debt.terminated_date
        return client.debt, overdue, weekly_payment
    except Exception as err:
        print(err)
    return 0, False, None
