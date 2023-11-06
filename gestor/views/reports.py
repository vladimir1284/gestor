from datetime import datetime, timedelta, date
from django.conf import settings
from typing import List
from itertools import chain
from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models import Min
from inventory.models import ProductTransaction
from services.models import (
    Expense,
    PendingPayment,
    Payment,
    PaymentCategory,
)
from costs.models import Cost
from utils.models import Order
from services.views.order import (
    computeOrderAmount,
)
from gestor.views.utils import getWeek, getMonthYear
from rent.models.lease import (
    Due,
    Payment as RentalPayment,
    Lease,
)
from rent.views.client import get_start_paying_date
from datetime import datetime
from django.utils import timezone
import pytz
from dateutil.relativedelta import relativedelta


class UnknownCategory:
    id = -1
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
    """ 
    This function calculates the balance of an order by computing the
    transactions, services, and expenses associated with it. It then computes
    the labor income, consumables and parts, and third party expenses. The
    product transactions are used to update the product dictionary, which
    stores information about the products involved in the order. The function
    also updates the order object with the parts cost, consumable expenses,
    third party expenses, net amount, and tax amount. Overall, this function
    provides a comprehensive view of the financial aspects of an order.
    """

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
def monthly_report(request, year=None, month=None):
    """
    The function takes optional parameters for the year and month, allowing
    the user to specify the time period for the report. If no parameters are
    provided, the function will default to the current year and month.

    The function begins by calculating the previous, current, and next months
    and years based on the provided or default values. It then retrieves a
    list of completed sell orders for the specified month and year, excluding
    any orders associated with a membership. The orders are sorted in
    descending order based on the termination date.

    Next, the function retrieves a list of costs for the specified month and
    year, sorted in descending order by date. It also retrieves a list of
    pending payments for the specified month and year, sorted by the creation
    date in descending order.

    The function then calls the "computeReport" function to compute the
    necessary data for the report. The computed data is stored in the
    "context" dictionary.

    Finally, the function sets additional values in the "context" dictionary,
    such as the previous and next months and years, and the total membership
    for the current month and year. It renders the "monthly.html" template,
    passing the "context" dictionary as the context.

    Overall, this function provides a convenient way to generate monthly
    reports with relevant data for analysis and decision-making.
    """

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
        company__membership=True, associated=None)

    costs = Cost.objects.filter(date__year=currentYear,
                                date__month=currentMonth).order_by("-date")

    pending_payments = PendingPayment.objects.filter(
        created_date__year=currentYear,
        created_date__month=currentMonth).order_by("-created_date")

    context = computeReport(orders, costs, pending_payments)
    context.setdefault('previousMonth', previousMonth)
    context.setdefault('currentMonth', currentMonth)
    context.setdefault('nextMonth', nextMonth)
    context.setdefault('thisMonth', datetime.now().month)
    context.setdefault('previousYear', previousYear)
    context.setdefault('currentYear', currentYear)
    context.setdefault('nextYear', nextYear)
    context.setdefault('thisYear', datetime.now().year)
    context.setdefault('interval', 'monthly')

    context.setdefault('membership', getMonthlyMembership(
        currentYear, currentMonth, all=True)['total']['gross'])

    return render(request, 'monthly.html', context)


def getRentalReport(currentYear, currentMonth):
    paid_dues = Due.objects.filter(
        due_date__year=currentYear,
        due_date__month=currentMonth)
    invoice_income = paid_dues.aggregate(total=Sum('amount'))['total']
    total_income = RentalPayment.objects.filter(
        date_of_payment__year=currentYear,
        date_of_payment__month=currentMonth).aggregate(total=Sum('amount'))['total']
    # Unpaid dues
    leases = Lease.objects.filter(contract__stage="active")
    unpaid_amount = 0
    unpaid_leases = []
    for lease in leases:
        interval_start = get_start_paying_date(lease)
        first_day_of_this_month = timezone.make_aware(timezone.datetime(
            currentYear, currentMonth, 1), pytz.timezone(settings.TIME_ZONE))
        first_day_of_next_month = first_day_of_this_month + \
            relativedelta(months=1)

        interval_start = max(first_day_of_this_month, interval_start)
        interval_end = min(first_day_of_next_month, timezone.now())
        occurrences = lease.event.get_occurrences(interval_start,
                                                  interval_end)
        lease.unpaid_dues = []
        unpaid_lease = False
        for occurrence in occurrences:
            paid_due = Due.objects.filter(due_date=occurrence.start.date(),
                                          lease=lease)
            if len(paid_due) == 0:
                unpaid_amount += lease.payment_amount
                lease.unpaid_dues.append(occurrence)
                unpaid_lease = True
        if unpaid_lease:
            unpaid_leases.append(lease)

    rental = {
        'paid_dues': paid_dues,
        'total_income': total_income,
        'invoice_income': invoice_income,
        'unpaid_amount': unpaid_amount,
        'planned_income': unpaid_amount+invoice_income,
        'unpaid_leases': unpaid_leases,
        'pending_payments': total_income-float(invoice_income),
    }
    return rental


@login_required
def monthly_payments(request, category_id, year, month):
    category = get_object_or_404(PaymentCategory, id=category_id)

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
        company__membership=True, associated=None)

    pending_payments = PendingPayment.objects.filter(
        category=category,
        created_date__year=currentYear,
        created_date__month=currentMonth).order_by("-created_date")

    context = getPaymentContext(orders, category, pending_payments)

    return render(request, 'payments.html', context)


@login_required
def weekly_membership_report(request, date=None):

    (start_date, end_date, previousWeek, nextWeek) = getWeek(date)

    context = getWeekMembership(start_date, end_date)

    context.setdefault('start_date', start_date)
    context.setdefault('end_date', end_date - timedelta(days=1))
    context.setdefault('previousWeek', previousWeek.strftime("%m%d%Y"))
    context.setdefault('nextWeek', nextWeek.strftime("%m%d%Y"))
    return render(request, 'weekly_membership.html', context)


def getWeekMembership(start_date, end_date):
    """
    The given code is a function named "getWeekMembership" that takes two
    parameters: "start_date" and "end_date".
     The function retrieves a list of completed sell orders from the database,
    filtered by the specified start and end dates. The orders are then sorted
    in descending order based on their termination date.
     The function also excludes any orders that belong to companies with a
    membership set to False, as well as any orders that have no associated
    company.
     Additionally, the function retrieves a list of costs and pending payments
    from the database, filtered by the specified start and end dates. The
    costs are sorted in descending order based on their date.
     Finally, the function calls another function named "computeReport" and
    passes the retrieved orders, costs, and pending payments as arguments.
    The result of the "computeReport" function is returned as the output of
    the "getWeekMembership" function. 
    """

    orders = Order.objects.filter(
        status='complete',
        type='sell',
        terminated_date__gt=start_date,
        terminated_date__lte=end_date).order_by(
        '-terminated_date').exclude(
        company__membership=False).exclude(
        company=None)

    costs = Cost.objects.filter(date__range=(
        start_date, end_date)).order_by("-date")

    pending_payments = PendingPayment.objects.filter(
        created_date__gt=start_date,
        created_date__lte=end_date).order_by("-created_date")

    return computeReport(orders, costs, pending_payments)


@login_required
def monthly_membership_report(request, year=None, month=None):
    # Prepare dashboard from last close
    ((previousMonth, previousYear),
        (currentMonth, currentYear),
        (nextMonth, nextYear)) = getMonthYear(month, year)

    context = getMonthlyMembership(currentYear, currentMonth)

    context.setdefault('previousMonth', previousMonth)
    context.setdefault('currentMonth', currentMonth)
    context.setdefault('nextMonth', nextMonth)
    context.setdefault('thisMonth', datetime.now().month)
    context.setdefault('previousYear', previousYear)
    context.setdefault('currentYear', currentYear)
    context.setdefault('nextYear', nextYear)
    context.setdefault('thisYear', datetime.now().year)
    context.setdefault('rental', getRentalReport(currentYear, currentMonth))

    return render(request, 'monthly_membership.html', context)


def getMonthlyMembership(currentYear, currentMonth, all=False):
    orders = Order.objects.filter(
        status='complete',
        type='sell',
        terminated_date__year=currentYear,
        terminated_date__month=currentMonth).order_by(
        '-terminated_date').exclude(
        company__membership=False).exclude(
        company=None).exclude(
        associated__isnull=False)
    # Separate initial orders only for Rental Report
    if not all:
        orders.has_initial = False
        for order in orders:
            first_terminated_date = Order.objects.filter(
                trailer=order.trailer).aggregate(oldest=Min('terminated_date'))['oldest']
            order.is_initial = (order.terminated_date == first_terminated_date)
            if order.is_initial:
                orders.has_initial = True

    costs = Cost.objects.filter(date__year=currentYear,
                                date__month=currentMonth).order_by("-date")

    pending_payments = PendingPayment.objects.filter(
        created_date__year=currentYear,
        created_date__month=currentMonth).order_by("-created_date")
    return computeReport(orders, costs, pending_payments)


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
        company__membership=True, associated=None)

    costs = Cost.objects.filter(date__range=(
        start_date, end_date)).order_by("-date")

    pending_payments = PendingPayment.objects.filter(
        created_date__gt=start_date,
        created_date__lte=end_date).order_by("-created_date")

    context = computeReport(orders, costs, pending_payments)
    context.setdefault('now', datetime.now())
    context.setdefault('start_date', start_date)
    context.setdefault('end_date', end_date - timedelta(days=1))
    context.setdefault('currentDate', start_date.strftime("%m%d%Y"))
    context.setdefault('previousWeek', previousWeek.strftime("%m%d%Y"))
    context.setdefault('nextWeek', nextWeek.strftime("%m%d%Y"))
    context.setdefault('interval', 'weekly')

    context.setdefault('membership', getWeekMembership(
        start_date, end_date)['total']['gross'])

    return render(request, 'weekly.html', context)


@login_required
def weekly_payments(request, category_id, date):
    category = get_object_or_404(PaymentCategory, id=category_id)

    (start_date, end_date, previousWeek, nextWeek) = getWeek(date)

    orders = Order.objects.filter(
        status='complete',
        type='sell',
        terminated_date__gt=start_date,
        terminated_date__lte=end_date).order_by(
        '-terminated_date').exclude(
        associated__membership=True).exclude(
        company__membership=True, associated=None)

    pending_payments = PendingPayment.objects.filter(
        category=category,
        created_date__gt=start_date,
        created_date__lte=end_date).order_by("-created_date")

    context = getPaymentContext(orders, category, pending_payments)

    return render(request, 'payments.html', context)


def getPaymentContext(orders, category, pending_payments):
    """ 
    Overall, this function is useful for obtaining the payment context for a 
    specific category and set of orders, including both completed payments and 
    pending payments.
    This function retrieves the payment context for a given set of orders, a 
    specified category, and a list of pending payments. It first filters the 
    Payment objects based on the provided orders and category. Then, it 
    calculates the total amount by iterating over the retrieved payments and 
    adding up their amounts. Next, it adds the amounts of the pending payments 
    to the total. The function returns a dictionary containing the retrieved 
    payments, the total amount, the number of transactions (which is the sum of 
    the retrieved payments and the pending payments), the list of pending 
    payments, and the specified category. 
   """
    payments = Payment.objects.filter(order__in=orders,
                                      category=category)
    total = 0
    for payment in payments:
        total += payment.amount

    for payment in pending_payments:
        total += payment.amount

    return {'payments': payments,
            'total': total,
            'transactions': len(payments) + len(pending_payments),
            'pending_payments': pending_payments,
            'category': category}


def computeReport(orders, costs, pending_payments):
    """ 
    The function  `computeReport`  is designed to generate a report based on 
    several parameters: orders, costs, and pending payments. 
    The function first initializes a number of variables to track various 
    aspects of the orders, such as the number of parts and consumables, the 
    gross and net amounts, taxes, discounts, and third-party costs. It also 
    creates a dictionary to store product information. 
    Next, the function iterates over each order. For each order, it updates the 
    respective variables and calculates the order balance. It also fetches all 
    payments associated with the order.
    Then, the function calculates the total costs and categorizes them. It sorts 
    the categories based on the amount and prepares them for chart representation. 
    If there are more than 4 categories, it groups the remaining ones under 
    "Others".
    The function then calculates the profit for each product type (parts and 
    consumables) and sorts the products based on profit. It also calculates the 
    efficiency of each product.
    Next, it handles the payments. It fetches all payments associated with the 
    orders and includes any pending payments. It calculates the total payment 
    amount and the amount of debt paid. It categorizes the payments and sorts them 
    based on the amount. It also prepares the payment categories for chart 
    representation, grouping any extra categories under "Others".
    Finally, the function returns a dictionary containing all the calculated and 
    sorted data, which can be used to generate a detailed report.
    """
    parts = 0
    consumable = 0
    gross = 0
    third_party = 0
    net = 0
    labor = 0
    tax = 0
    discount = 0
    parts_initial = 0
    consumable_initial = 0
    gross_initial = 0
    third_party_initial = 0
    net_initial = 0
    labor_initial = 0
    tax_initial = 0
    discount_initial = 0
    products = {}
    orders.labor = 0

    for order in orders:
        getOrderBalance(order, products)
        orders.labor += order.labor
        if order.is_initial:
            parts_initial += order.parts
            consumable_initial += order.consumable
            gross_initial += order.amount
            third_party_initial += order.third_party
            net_initial += order.net
            labor_initial += order.labor
            tax_initial += order.tax
            discount_initial += order.discount
        else:
            parts += order.parts
            consumable += order.consumable
            gross += order.amount
            third_party += order.third_party
            net += order.net
            labor += order.labor
            tax += order.tax
            discount += order.discount

        # Payments
        order.payments = Payment.objects.filter(order=order)

    total = {
        'parts': parts,
        'consumable': consumable,
        'gross': gross,
        'third_party': third_party,
        'net': net,
        'labor': labor,
        'discount': discount,
        'tax': tax,
    }
    total_initial = {
        'parts': parts_initial,
        'consumable': consumable_initial,
        'gross': gross_initial,
        'third_party': third_party_initial,
        'net': net_initial,
        'labor': labor_initial,
        'discount': discount_initial,
        'tax': tax_initial,
    }
    # Costs
    costs.total = 0
    cats = {}
    for cost in costs:
        category = cost.category or unknownCategory
        if category not in cats.keys():
            cats.setdefault(category, [cost.amount, 1])
        else:
            cats[category][0] += cost.amount
            cats[category][1] += 1
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
            product.average_price = product.price/product.quantity
            product.average_cost = product.cost/product.quantity
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
            payment_cats.setdefault(category, [payment.amount, 0, 0, 1, 0, 0])
        else:
            payment_cats[category][0] += payment.amount
            payment_cats[category][3] += 1

        payment_total += payment.amount

        if isinstance(payment, PendingPayment):
            debt_paid += payment.amount
            payment_cats[category][1] += payment.amount
            payment_cats[category][4] += 1
        else:
            payment_cats[category][2] += payment.amount
            payment_cats[category][5] += 1

    # Sort by amount
    sorted_payment_cats = sorted(
        payment_cats, key=lambda cat: payment_cats[cat][0], reverse=True)

    extra_charge = 0
    chart_payments = []
    othersCategory = UnknownCategory("Others", '#8592a3')

    for i, cat in enumerate(sorted_payment_cats):
        cat.style = STYLE_COLOR[cat.chartColor]
        cat.amount = payment_cats[cat][0]
        cat.amount_payment = payment_cats[cat][1]
        cat.amount_service = payment_cats[cat][2]
        if cat.extra_charge > 0:
            cat.extra_charge = cat.amount*cat.extra_charge/100
            # cat.amount += cat.extra_charge
            extra_charge += cat.extra_charge

        cat.transactions = payment_cats[cat][3]
        cat.payments = payment_cats[cat][4]
        cat.services = payment_cats[cat][5]

        if i > 2 and len(sorted_payment_cats) > 4:
            othersCategory.amount += cat.amount
        else:
            chart_payments.append(cat)

    if len(sorted_payment_cats) > 4:
        chart_payments.append(othersCategory)

    return {
        'orders': orders,
        'total': total,
        'total_initial': total_initial,
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
    """
    Procedure for computing profit
    min    - Discount the product minimum price
    profit - Compute total profit
    """
    if procedure == "min":
        return (transaction.getAmount()
                - transaction.getMinCost())
    if procedure == "profit":
        return (transaction.getAmount()
                - transaction.cost)
