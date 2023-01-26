import datetime
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from inventory.models import ProductTransaction
from services.models import Expense, ServiceTransaction
from costs.models import Cost
from utils.models import Order
from services.views import (
    computeOrderAmount,  # TODO remove this import and make a custom function here
)


def getOrderBalance(order: Order, products: dict):
    computeOrderAmount(order)
    # Consumables and parts
    transactions = ProductTransaction.objects.filter(order=order)
    parts_cost = 0
    consumable_expenses = 0
    for trans in transactions:
        product = trans.product
        if product in products.keys():
            products[product]['quantity'] += trans.quantity
            products[product]['profit'] += computeTransactionProfit(trans)
        else:
            products.setdefault(product, {
                'type': product.type,
                'name': product.name,
                'unit': product.unit,
                'quantity': trans.quantity,
                'profit': computeTransactionProfit(trans)
            })
        if product.type == 'part':
            parts_cost += trans.getMinCost()
        if product.type == 'consumable':
            consumable_expenses += trans.cost
    # Third party expenses
    tpe = Expense.objects.filter(order=order)
    third_party_expenses = 0
    for expense in tpe:
        third_party_expenses += expense.cost

    # Load balance in order
    order.parts = parts_cost
    order.consumable = consumable_expenses
    order.third_party = third_party_expenses
    order.net = (order.amount
                 - order.parts
                 - order.consumable
                 - order.third_party
                 )
    order.amount += order.tax


@login_required
def dashboard(request):
    if (request.user.profile_user.role == 2):  # Mechanic
        return redirect('list-service-order')
    else:
        # Prepare dashboard from last close
        orders = Order.objects.filter(
            status='complete',
            type='sell',
            terminated_date__gte=datetime.datetime(
                2010, 1, 1, 0, 0,
                tzinfo=datetime.timezone.utc)).order_by(
                    '-terminated_date').exclude(
                        associated__membership=True).exclude(
                            company__membership=True)
        parts = 0
        consumable = 0
        gross = 0
        third_party = 0
        net = 0
        tax = 0
        products = {}
        for order in orders:
            getOrderBalance(order, products)
            parts += order.parts
            consumable += order.consumable
            gross += order.amount
            third_party += order.third_party
            net += order.net
            tax += order.tax
        total = {
            'parts': parts,
            'consumable': consumable,
            'gross': gross,
            'third_party': third_party,
            'net': net,
            'tax': tax,
        }
        # Costs
        costs = Cost.objects.all().order_by("-date")
        costs.total = 0
        for cost in costs:
            costs.total += cost.amount

        # Product incomes
        parts_profit = 0
        consumables_profit = 0
        for product in products.keys():
            if product.type == "part":
                parts_profit += products[product]['profit']
            if product.type == "consumable":
                consumables_profit += products[product]['profit']

        context = {
            'orders': orders,
            'total': total,
            'costs': costs,
            'products': products.values(),
            'parts_profit': parts_profit,
            'consumables_profit': consumables_profit,
        }
        return render(request, 'dashboard.html', context)


def computeTransactionProfit(transaction: ProductTransaction):
    return (transaction.getAmount()
            - transaction.getMinCost())
