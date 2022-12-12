import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from inventory.models import ProductTransaction
from services.models import Expense, ServiceTransaction
from utils.models import Order


@login_required
def dashboard(request):
    # Prepare dashboard from last close
    orders = Order.objects.filter(
        type='sell', terminated_date__gte=datetime.date(2011, 1, 1)).order_by(
            '-terminated_date'
    )
    parts = 0
    consumable = 0
    service = 0
    third_party = 0
    for order in orders:
        getOrderBalance(order)
        parts += order.parts
        consumable += order.consumable
        service += order.service
        third_party += order.third_party
    # Incomes
    gross_income = parts + service
    net_income = gross_income-(consumable+third_party)

    context = {
        'orders': orders,
        'parts': parts,
        'consumable': consumable,
        'service': service,
        'third_party': third_party,
        'gross_income': gross_income,
        'net_income': net_income,
    }
    return render(request, 'dashboard.html', context)


def getOrderBalance(order: Order):
    # Parts and consumables
    pt = ProductTransaction.objects.filter(order=order)
    parts_income = 0
    consumable_expenses = 0
    for transaction in pt:
        product = transaction.product
        if product.type == 'part':
            parts_income += transaction.price*transaction.quantity
        if product.type == 'consumable':
            consumable_expenses += product.stock_price/product.quantity*transaction.quantity
    # Services
    st = ServiceTransaction.objects.filter(order=order)
    service_income = 0
    for transaction in st:
        service_income += transaction.price*transaction.quantity
    # Third party expenses
    tpe = Expense.objects.filter(order=order)
    third_party_expenses = 0
    for expense in tpe:
        third_party_expenses += expense.cost

    # Load balance in order
    order.parts = parts_income
    order.consumable = consumable_expenses
    order.service = service_income
    order.third_party = third_party_expenses
