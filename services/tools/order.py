from datetime import datetime
from datetime import timedelta

import pytz

from inventory.models import ProductTransaction
from services.models import DebtStatus
from services.models import Expense
from services.models import Order
from services.models import Payment
from services.models import ServiceTransaction
from services.tools.transaction import check_transaction
from utils.models import Associated


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


def computeOrderAmount(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    transactions.satisfied = True
    transactions.usParts = False
    transactions.usConsumable = False
    services = ServiceTransaction.objects.filter(order=order)
    expenses = Expense.objects.filter(order=order)
    # Compute amount
    tax = 0
    parts_amount = 0
    service_amount = 0
    for transaction in transactions:
        # count = transaction.product.computeAvailable()
        # transaction.satisfied = count >= 0
        transaction.satisfied = check_transaction(transaction)
        if not transaction.satisfied:
            transactions.satisfied = False
            if transaction.product.type == "consumable":
                transactions.usConsumable = True
            else:
                transactions.usParts = True

        transaction.amount = transaction.getAmount()
        parts_amount += transaction.amount
        transaction.total_tax = transaction.getTax()
        tax += transaction.total_tax
    for service in services:
        service.amount = service.getAmount()
        service_amount += service.amount
        service.total_tax = service.getTax()
        tax += service.total_tax
    expenses.amount = 0
    for expense in expenses:
        expenses.amount += expense.cost
    amount = expenses.amount + service_amount + parts_amount
    order.amount = amount
    order.tax = tax
    order.service_amount = service_amount
    order.parts_amount = parts_amount
    return (transactions, services, expenses)


def getOrderContext(order_id):
    order = Order.objects.get(id=order_id)
    (transactions, services, expenses) = computeOrderAmount(order)
    satisfied = transactions.satisfied
    unsatisfiedParts = transactions.usParts
    unsatisfiedConsumable = transactions.usConsumable
    # Order by amount
    transactions = list(transactions)
    # Costs
    parts_cost = 0
    consumable_cost = 0
    # Count consumables and parts
    consumable_amount = 0
    parts_amount = 0
    consumable_tax = 0
    parts_tax = 0
    consumables = False
    # Costs
    uparts_cost = 0
    uconsumable_cost = 0
    # Count consumables and parts
    uconsumable_amount = 0
    uparts_amount = 0
    uconsumable_tax = 0
    uparts_tax = 0

    for trans in transactions:
        if trans.product.type == "part":
            if trans.satisfied:
                parts_amount += trans.amount
                parts_tax += trans.total_tax
                parts_cost += trans.getMinCost()
            else:
                uparts_amount += trans.amount
                uparts_tax += trans.total_tax
                uparts_cost += trans.getMinCost()
        elif trans.product.type == "consumable":
            consumables = True
            if trans.satisfied:
                consumable_amount += trans.amount
                consumable_tax += trans.total_tax
                if trans.cost is not None:
                    consumable_cost += trans.cost
            else:
                uconsumable_amount += trans.amount
                uconsumable_tax += trans.total_tax
                if trans.cost is not None:
                    uconsumable_cost += trans.cost
    # Account services
    service_amount = 0
    service_tax = 0
    for service in services:
        service_amount += service.amount
        service_tax += service.total_tax
    # Terminated order
    terminated = order.status in ["decline", "complete"]
    empty = (len(services) + len(transactions)) == 0
    # Compute totals
    order.total = order.amount + order.tax - order.discount
    consumable_total = consumable_tax + consumable_amount
    parts_total = parts_amount + parts_tax
    service_total = service_amount + service_tax
    uparts_total = uparts_amount + uparts_tax
    uconsumable_total = uconsumable_tax + uconsumable_amount
    # Compute tax percent
    tax_percent = 8.25

    # Profit
    profit = order.amount - expenses.amount - consumable_cost - parts_cost

    if order.associated:
        if order.associated.debt > 0:
            order.associated.debt_status = DebtStatus.objects.filter(
                client=order.associated
            )[0].status
    try:
        order.associated.phone_number = order.associated.phone_number.as_national
    except:
        pass
    return {
        "order": order,
        "services": services,
        "satisfied": satisfied,
        "unsatisfiedParts": unsatisfiedParts,
        "unsatisfiedConsumable": unsatisfiedConsumable,
        "service_amount": service_amount,
        "service_total": service_total,
        "service_tax": service_tax,
        "expenses": expenses,
        "expenses_amount": expenses.amount,
        "transactions": transactions,
        "consumable_amount": consumable_amount,
        "consumable_total": consumable_total,
        "consumable_tax": consumable_tax,
        "parts_amount": parts_amount,
        "parts_total": parts_total,
        "parts_tax": parts_tax,
        "uconsumable_amount": uconsumable_amount,
        "uconsumable_total": uconsumable_total,
        "uconsumable_tax": uconsumable_tax,
        "uparts_amount": uparts_amount,
        "uparts_total": uparts_total,
        "uparts_tax": uparts_tax,
        "terminated": terminated,
        "empty": empty,
        "tax_percent": tax_percent,
        "consumables": consumables,
        "profit": profit,
    }
