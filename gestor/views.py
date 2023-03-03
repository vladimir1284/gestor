import datetime
from typing import List
from collections import OrderedDict
from operator import itemgetter, attrgetter
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from inventory.models import ProductTransaction
from services.models import Expense, ServiceTransaction
from costs.models import Cost
from utils.models import Order, Transaction
from services.views import (
    computeOrderAmount,  # TODO remove this import and make a custom function here
)


def getOrderBalance(order: Order, products: dict):
    computeOrderAmount(order)
    # Consumables and parts
    transactions: List[ProductTransaction] = ProductTransaction.objects.filter(
        order=order)
    parts_cost = 0
    consumable_expenses = 0
    for trans in transactions:
        product = trans.product
        if product in products.keys():
            products[product]['quantity'] += trans.quantity
            products[product]['profit'] += computeTransactionProfit(
                trans,
                procedure="profit")
        else:
            products.setdefault(product, {
                'type': product.type,
                'name': product.name,
                'unit': product.unit,
                'quantity': trans.quantity,
                'profit': computeTransactionProfit(trans, procedure="profit")
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
def report(request, year, month):
    # Prepare dashboard from last close
    ((previousMonth, previousYear),
        (currentMonth, currentYear),
        (nextMonth, nextYear)) = getMonthYear(month, year)

    orders = Order.objects.filter(
        status='complete',
        type='sell',
        terminated_date__year=currentYear,
        terminated_date__month=currentMonth).order_by(
        '-terminated_date').exclude(
        associated__membership=True).exclude(
        company__membership=True)

    costs = Cost.objects.filter(date__year=currentYear,
                                date__month=currentMonth).order_by("-date")

    context = computeReport(orders, costs)
    context.setdefault('previousMonth', previousMonth)
    context.setdefault('currentMonth', currentMonth)
    context.setdefault('nextMonth', nextMonth)
    context.setdefault('previousYear', previousYear)
    context.setdefault('currentYear', currentYear)
    context.setdefault('nextYear', nextYear)
    return render(request, 'dashboard.html', context)


@login_required
def dashboard(request):
    if (request.user.profile_user.role == 2):  # Mechanic
        return redirect('list-service-order')
    else:
        return report(request, year=None, month=None)


def computeReport(orders, costs):
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

    # Sort by profit
    sorted_products = sorted(
        products, key=lambda product: products[product]['profit'], reverse=True)

    for product in sorted_products:
        product.profit = products[product]['profit']
        product.quantity = products[product]['quantity']

    return {
        'orders': orders,
        'total': total,
        'costs': costs,
        'products': sorted_products,
        'parts_profit': parts_profit,
        'consumables_profit': consumables_profit,
    }


def computeTransactionProfit(transaction: ProductTransaction, procedure="min"):
    # Procedure for computing profit
    # min    - Discount the product minimum price
    # profit - Compute total profit
    if procedure == "min":
        return (transaction.getAmount()
                - transaction.getMinCost())
    if procedure == "profit":
        return (transaction.getAmount()
                - transaction.cost)


def getMonthYear(month=None, year=None):
    # Current
    if month is None:
        currentMonth = datetime.datetime.now().month
    else:
        month = int(month)
        if month > 12 or month < 0:
            raise ValueError(F'Wrong month value: {month}!')
        currentMonth = month
    if year is None:
        currentYear = datetime.datetime.now().year
    else:
        year = int(year)
        currentYear = year

    # Next
    nextYear = currentYear
    nextMonth = currentMonth + 1
    if nextMonth > 12:
        nextMonth = 1
        nextYear = currentYear+1

    # Previous
    previousYear = currentYear
    previousMonth = currentMonth - 1
    if previousMonth < 1:
        previousMonth = 12
        previousYear = currentYear-1

    return ((previousMonth, previousYear), (currentMonth, currentYear), (nextMonth, nextYear))
