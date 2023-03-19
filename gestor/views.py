from datetime import datetime, timedelta
from typing import List
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
    (transactions, services, expenses) = computeOrderAmount(order)

    # compute labor income
    order.labor = -order.discount
    for service in services:
        order.labor += service.amount

    # Consumables and parts
    transactions: List[ProductTransaction] = ProductTransaction.objects.filter(
        order=order)
    parts_cost = 0
    consumable_expenses = 0
    for trans in transactions:
        product = trans.product
        if product in products.keys():
            products[product]['quantity'] += trans.quantity
            products[product]['cost'] += trans.cost
            products[product]['profit'] += computeTransactionProfit(
                trans,
                procedure="profit")
        else:
            products.setdefault(product, {
                'type': product.type,
                'name': product.name,
                'unit': product.unit,
                'quantity': trans.quantity,
                'cost': trans.cost,
                'profit': computeTransactionProfit(trans, procedure="profit")
            })
        if product.type == 'part':
            parts_cost += trans.cost
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
    order.amount -= order.discount
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
def weekly_report(request, date=None):

    (start_date, end_date, previousWeek, nextWeek) = getWeek(date)

    orders = Order.objects.filter(
        status='complete',
        type='sell',
        terminated_date__gt=start_date,
        terminated_date__lte=end_date).order_by(
        '-terminated_date').exclude(
        associated__membership=True).exclude(
        company__membership=True)

    costs = Cost.objects.filter(date__gt=start_date,
                                date__lte=end_date).order_by("-date")

    context = computeReport(orders, costs)
    context.setdefault('start_date', start_date)
    context.setdefault('end_date', end_date)
    context.setdefault('previousWeek', previousWeek.strftime("%m%d%Y"))
    context.setdefault('nextWeek', nextWeek.strftime("%m%d%Y"))
    return render(request, 'weekly.html', context)


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
    discount = 0
    products = {}
    orders.labor = 0
    for order in orders:
        getOrderBalance(order, products)
        orders.labor += order.labor
        parts += order.parts
        consumable += order.consumable
        gross += order.amount
        third_party += order.third_party
        net += order.net
        tax += order.tax
        discount += order.discount

    total = {
        'parts': parts,
        'consumable': consumable,
        'gross': gross,
        'third_party': third_party,
        'net': net,
        'discount': discount,
        'tax': tax,
    }
    # Costs
    costs.total = 0
    cats = {}
    for cost in costs:
        if cost.category not in cats.keys():
            cats.setdefault(cost.category, [cost.amount, 1])
        else:
            cats[cost.category][0] += cost.amount
            cats[cost.category][1] += 1
        costs.total += cost.amount
    # Sort by amount
    sorted_cats = sorted(
        cats, key=lambda cat: cats[cat][0], reverse=True)

    for cat in sorted_cats:
        cat.amount = cats[cat][0]
        cat.items = cats[cat][1]

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
        product.cost = products[product]['cost']
        if products[product]['cost'] != 0:
            product.efficiency = int(
                100*products[product]['profit']/products[product]['cost'])
        else:
            product.efficiency = None

    return {
        'orders': orders,
        'total': total,
        'costs': costs,
        'cost_cats': sorted_cats,
        'profit': total['net'] - costs.total,
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


def getWeek(dt=None):
    if dt is None:
        dt = datetime.now()
    else:
        dt = datetime.strptime(dt, "%m%d%Y")
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=7)
    previousWeek = dt - timedelta(days=7)
    nextWeek = dt + timedelta(days=7)
    return (start.date(), end.date(), previousWeek, nextWeek)


def getMonthYear(month=None, year=None):
    # Current
    if month is None:
        currentMonth = datetime.now().month
    else:
        month = int(month)
        if month > 12 or month < 0:
            raise ValueError(F'Wrong month value: {month}!')
        currentMonth = month
    if year is None:
        currentYear = datetime.now().year
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
