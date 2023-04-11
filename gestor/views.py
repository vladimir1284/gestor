from datetime import datetime, timedelta
from typing import List
from itertools import chain
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from inventory.models import ProductTransaction
from services.models import (
    Expense,
    ServiceTransaction,
    PendingPayment,
    Payment
)
from costs.models import Cost
from utils.models import Order, Transaction
from services.views import (
    computeOrderAmount,  # TODO remove this import and make a custom function here
)


class UnknownCategory:
    name = "Unknown"
    extra_charge = 0
    amount = 0
    chartColor = "#233446"  # Dark

    def __init__(self, name=None, chartColor=None):
        if name is not None:
            self.name = name
        if chartColor is not None:
            self.chartColor = chartColor


unknownCategory = UnknownCategory()

STYLE_COLOR = {
    '#696cff': 'primary',
    '#8592a3': 'secondary',
    '#71dd37': 'success',
    '#ff3e1d': 'danger',
    '#ffab00': 'warning',
    '#03c3ec': 'info',
    '#233446': 'dark',
}


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
            products[product]['price'] += trans.getAmount()
            products[product]['profit'] += computeTransactionProfit(
                trans,
                procedure="profit")
        else:
            products.setdefault(product, {
                'type': product.type,
                'name': product.name,
                'unit': product.unit,
                'quantity': trans.quantity,
                'price': trans.getAmount(),
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

    pending_payments = PendingPayment.objects.filter(
        created_date__year=currentYear,
        created_date__month=currentMonth).order_by("-created_date")

    context = computeReport(orders, costs, pending_payments)
    context.setdefault('previousMonth', previousMonth)
    context.setdefault('currentMonth', currentMonth)
    context.setdefault('nextMonth', nextMonth)
    context.setdefault('previousYear', previousYear)
    context.setdefault('currentYear', currentYear)
    context.setdefault('nextYear', nextYear)
    return render(request, 'monthly.html', context)


@login_required
def weekly_membership_report(request, date=None):

    (start_date, end_date, previousWeek, nextWeek) = getWeek(date)

    orders = Order.objects.filter(
        status='complete',
        type='sell',
        terminated_date__gt=start_date,
        terminated_date__lte=end_date).order_by(
        '-terminated_date').exclude(
        company__membership=False).exclude(
        company=None)

    costs = Cost.objects.filter(date__gt=start_date,
                                date__lte=end_date).order_by("-date")

    context = computeReport(orders, costs)
    context.setdefault('start_date', start_date)
    context.setdefault('end_date', end_date - timedelta(days=1))
    context.setdefault('previousWeek', previousWeek.strftime("%m%d%Y"))
    context.setdefault('nextWeek', nextWeek.strftime("%m%d%Y"))
    return render(request, 'weekly_membership.html', context)


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

    pending_payments = PendingPayment.objects.filter(
        created_date__gt=start_date,
        created_date__lte=end_date).order_by("-created_date")

    context = computeReport(orders, costs, pending_payments)
    context.setdefault('start_date', start_date)
    context.setdefault('end_date', end_date - timedelta(days=1))
    context.setdefault('previousWeek', previousWeek.strftime("%m%d%Y"))
    context.setdefault('nextWeek', nextWeek.strftime("%m%d%Y"))
    return render(request, 'weekly.html', context)


@login_required
def dashboard(request):
    if (request.user.profile_user.role == 2):  # Mechanic
        return redirect('list-service-order')
    else:
        return report(request, year=None, month=None)


def computeReport(orders, costs, pending_payments):
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

    otherCosts = UnknownCategory("Others", '#8592a3')
    chart_costs = []

    for i, cat in enumerate(sorted_cats):
        cat.style = STYLE_COLOR[cat.chartColor]
        cat.amount = cats[cat][0]
        cat.items = cats[cat][1]

        if i > 2 and len(sorted_cats) > 4:
            otherCosts.amount += cat.amount
        else:
            chart_costs.append(cat)

    if len(sorted_cats) > 4:
        chart_costs.append(otherCosts)

    # Product incomes
    parts_profit = 0
    parts_price = 0
    parts_cost = 0
    consumables_profit = 0
    for product in products.keys():
        if product.type == "part":
            parts_profit += products[product]['profit']
            parts_price += products[product]['price']
            parts_cost += products[product]['cost']
        if product.type == "consumable":
            consumables_profit += products[product]['profit']

    parts_utility = 0
    if (parts_cost != 0):
        parts_utility = 100*parts_profit/parts_cost

    # Sort by profit
    sorted_products = sorted(
        products, key=lambda product: products[product]['profit'], reverse=True)

    for product in sorted_products:
        product.profit = products[product]['profit']
        product.quantity = products[product]['quantity']
        product.cost = products[product]['cost']
        product.price = products[product]['price']
        if product.quantity > 0:
            product.average = product.price/product.quantity
        if products[product]['cost'] != 0:
            product.efficiency = int(
                100*products[product]['profit']/products[product]['cost'])
        else:
            product.efficiency = None

    # Payments
    payments = Payment.objects.filter(order__in=orders)  # Order payments
    payments = list(chain(payments, pending_payments))  # Include debt payments

    payment_total = 0
    debt_paid = 0
    payment_cats = {}
    for payment in payments:
        if payment.category is None:
            category = unknownCategory
        else:
            category = payment.category
        if category not in payment_cats.keys():
            payment_cats.setdefault(category, [payment.amount, 1])
        else:
            payment_cats[category][0] += payment.amount
            payment_cats[category][1] += 1
        payment_total += payment.amount
        if isinstance(payment, PendingPayment):
            debt_paid += payment.amount

    # Sort by amount
    sorted_payment_cats = sorted(
        payment_cats, key=lambda cat: payment_cats[cat][0], reverse=True)

    extra_charge = 0
    chart_payments = []
    othersCategory = UnknownCategory("Others", '#8592a3')

    for i, cat in enumerate(sorted_payment_cats):
        cat.style = STYLE_COLOR[cat.chartColor]
        cat.amount = payment_cats[cat][0]
        if cat.extra_charge > 0:
            cat.extra_charge = cat.amount*cat.extra_charge/100
            # cat.amount += cat.extra_charge
            extra_charge += cat.extra_charge
        cat.transactions = payment_cats[cat][1]

        if i > 2 and len(sorted_payment_cats) > 4:
            othersCategory.amount += cat.amount
        else:
            chart_payments.append(cat)

    if len(sorted_payment_cats) > 4:
        chart_payments.append(othersCategory)

    return {
        'orders': orders,
        'total': total,
        'costs': costs,
        'cost_cats': sorted_cats,
        'chart_costs': chart_costs,
        'payment_cats': sorted_payment_cats,
        'payment_total': payment_total,
        'chart_payments': chart_payments,
        'debt_paid': debt_paid,
        'payment_transactions': len(payments),
        'profit': total['net'] - costs.total,
        'products': sorted_products,
        'parts_profit': parts_profit,
        'parts_cost': parts_cost,
        'parts_utility': parts_utility,
        'parts_price': parts_price,
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
