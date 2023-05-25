from datetime import datetime, timedelta
from django.conf import settings
from typing import List
from itertools import chain
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import openai

from inventory.models import ProductTransaction, Product
from services.models import (
    Expense,
    ServiceTransaction,
    PendingPayment,
    Payment,
    PaymentCategory,
)
from costs.models import Cost
from utils.models import Order, Statistics
from users.views import get_debtor
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
def monthly_report(request, year=None, month=None):
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

    context.setdefault('membership', getMonthlyMembership(
        currentYear, currentMonth)['total']['gross'])

    return render(request, 'monthly.html', context)


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
        company__membership=True)

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
    context.setdefault('previousYear', previousYear)
    context.setdefault('currentYear', currentYear)
    context.setdefault('nextYear', nextYear)
    return render(request, 'monthly_membership.html', context)


def getMonthlyMembership(currentYear, currentMonth):
    orders = Order.objects.filter(
        status='complete',
        type='sell',
        terminated_date__year=currentYear,
        terminated_date__month=currentMonth).order_by(
        '-terminated_date').exclude(
        company__membership=False).exclude(
        company=None)

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
        company__membership=True)

    costs = Cost.objects.filter(date__gt=start_date,
                                date__lte=end_date).order_by("-date")

    pending_payments = PendingPayment.objects.filter(
        created_date__gt=start_date,
        created_date__lte=end_date).order_by("-created_date")

    context = computeReport(orders, costs, pending_payments)
    context.setdefault('start_date', start_date)
    context.setdefault('end_date', end_date - timedelta(days=1))
    context.setdefault('currentDate', start_date.strftime("%m%d%Y"))
    context.setdefault('previousWeek', previousWeek.strftime("%m%d%Y"))
    context.setdefault('nextWeek', nextWeek.strftime("%m%d%Y"))

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
        company__membership=True)

    pending_payments = PendingPayment.objects.filter(
        category=category,
        created_date__gt=start_date,
        created_date__lte=end_date).order_by("-created_date")

    context = getPaymentContext(orders, category, pending_payments)

    return render(request, 'payments.html', context)


def getPaymentContext(orders, category, pending_payments):
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


@login_required
def dashboard(request):
    N = 7  # number of weeks in the dashboard
    stats_list = weekly_stats(n=N)

    # Profit
    current_profit = stats_list[0].profit_before_costs - stats_list[0].costs
    previous_profit = stats_list[1].profit_before_costs - stats_list[1].costs
    profit_increment = 0
    if current_profit > 0:
        profit_increment = 100 * \
            (current_profit - previous_profit)/current_profit

    # Parts
    current_parts_profit = stats_list[0].parts_price - stats_list[0].parts_cost
    previous_parts_profit = stats_list[1].parts_price - \
        stats_list[1].parts_cost
    parts_profit_increment = 0
    if current_parts_profit > 0:
        parts_profit_increment = 100 * \
            (current_parts_profit - previous_parts_profit)/current_parts_profit

    # Costs
    current_costs = stats_list[0].costs
    previous_costs = stats_list[1].costs
    costs_increment = 0
    if current_costs > 0:
        costs_increment = 100 * \
            (current_costs - previous_costs)/current_costs

    # Debt balance
    current_debt_balance = stats_list[0].debt_created - stats_list[0].debt_paid
    previous_debt_balance = stats_list[1].debt_created - \
        stats_list[1].debt_paid
    debt_increment = 0
    if current_debt_balance > 0:
        debt_increment = 100*(current_debt_balance -
                              previous_debt_balance)/current_debt_balance
    # Stock costs
    current_stock_cost = Product.objects.aggregate(
        Sum("stock_price"))['stock_price__sum']

    # Purchase orders
    (start_date, end_date, previousWeek, nextWeek) = getWeek()  # This week
    (start_date, end_date, previousWeek, nextWeek) = getWeek(
        previousWeek.strftime("%m%d%Y"))  # Previous week
    purchase_orders = Order.objects.filter(status='complete',
                                           type='purchase',
                                           terminated_date__gt=start_date,
                                           terminated_date__lte=end_date)
    # Stock costs added
    transactions = ProductTransaction.objects.filter(
        order__in=purchase_orders)
    added = 0
    for trans in transactions:
        added += trans.getAmount()

    stock_cost_increment = 0

    if not current_stock_cost:
        current_stock_cost = 0
    else:
        stock_cost_increment = 100 * \
            (added - stats_list[0].parts_cost)/current_stock_cost

    # Time series
    stats_list.reverse()

    time_labels = [stats.date.strftime("%b, %d") for stats in stats_list]
    time_labels[0] = ""

    profit_data = [int(x.profit_before_costs - x.costs) for x in stats_list]
    parts_data = [int(x.parts_price - x.parts_cost) for x in stats_list]
    expenses_data = [int(x.costs) for x in stats_list]

    indicators = [
        {'name': 'Profit',
         'amount': current_profit,
         'increment': profit_increment,
         'positive': profit_increment > 0,
         'series': profit_data,
         'icon': 'images/icons/profit.png'},
        {'name': 'Parts',
         'amount': current_parts_profit,
         'increment': parts_profit_increment,
         'positive': parts_profit_increment > 0,
         'series': parts_data,
         'icon': 'images/icons/parts.jpg'},
        {'name': 'Expenses',
         'amount': current_costs,
         'increment': costs_increment,
         'positive': costs_increment < 0,
         'series': expenses_data,
         'icon': 'images/icons/costs.png'},
        {'name': 'Debt',
         'amount': current_debt_balance,
         'increment': debt_increment,
         'positive': debt_increment < 0,
         'series': None,
         'icon': 'images/icons/debt.png'},
        {'name': 'Stock',
         'amount': current_stock_cost,
         'increment': stock_cost_increment,
         'positive': stock_cost_increment < 0,
         'series': None,
         'icon': 'images/icons/inventory.png'},
    ]

    # Get gpt insights is needed
    if stats_list[-1].gpt_insights is None or stats_list[-1].gpt_insights == "":

        try:
            stats_list[-1].gpt_insights = get_gpt_insights(current_profit,
                                                           profit_increment,
                                                           current_parts_profit,
                                                           parts_profit_increment,
                                                           current_debt_balance,
                                                           debt_increment,
                                                           current_stock_cost,
                                                           stock_cost_increment,
                                                           N,
                                                           profit_data,
                                                           parts_data,
                                                           expenses_data)
            stats_list[0].save()
        except Exception as e:
            print(e)

    context = {
        'indicators': indicators,
        'last_date': stats_list[-1].date - timedelta(days=1),  # TODO fix this
        'time_labels': time_labels,
        'insights': stats_list[-1].gpt_insights
    }
    context = dict(context, **get_debtor(request))

    return render(request, 'dashboard.html', context)


def get_gpt_insights(current_profit,
                     profit_increment,
                     current_parts_profit,
                     parts_profit_increment,
                     current_debt_balance,
                     debt_increment,
                     current_stock_cost,
                     stock_cost_increment,
                     N,
                     profit_data,
                     parts_data,
                     expenses_data):

    prompt = F"""Using the following business data corresponding to the last week:
The total profit of the week was ${int(current_profit)}. 
The profit from parts sells of the week was ${int(current_parts_profit)}. 
The operational costs of the week where ${int(current_parts_profit)}. 
The debt balance of the week was ${int(current_debt_balance)}. 
The inventory costs this week is ${int(current_stock_cost)}. 
The average values for the last {int(N)} weeks is:
total profit: ${int(sum(profit_data) / len(profit_data))}
parts sell profit: ${int(sum(parts_data) / len(parts_data))}
operational costs: ${int(sum(expenses_data) / len(expenses_data))}
This is a repairs business for trailers and trucks called TOWITHOUSTON. 
The total profit includes the profit generated from the sell of parts, which are used in the repairs.
The debt accounts for the money that some clients left to be payed with in the next two weeks.

Create a summary paragraph for the user dashboard. 
Use rounded numbers only in the response. 
Use percentage when comparing to average values.
Do not use the data given above literally, since it is already shown in the page.
Use html format in your response for highlighting relevant data."""

    # Define additional options (optional)
    options = {
        'temperature': 0.5,
        'max_tokens': 1000,
        'top_p': 0.8,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0
    }
    openai.organization = settings.OPEN_AI_ORG
    openai.api_key = settings.OPENAI_API_KEY

    # Generate a completion
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        **options
    )

    # Access the generated text
    completion_text = response.choices[0].text.strip()
    return completion_text


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

        # Payments
        order.payments = Payment.objects.filter(order=order)

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
        if cat is not None:
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


def weekly_stats(date=None, n=12) -> List[Statistics]:
    # Compute weekly stats for a given date
    # Returns a list for several week stats
    # We get the data from the previous week

    (start_date, end_date, previousWeek, nextWeek) = getWeek(date)  # This week
    stats_list = []
    for _ in range(n):
        # Previous week
        (start_date, end_date, previousWeek, nextWeek) = getWeek(
            previousWeek.strftime("%m%d%Y"))

        try:
            # Weekly stats are stored in the end_date of the week
            stats = Statistics.objects.get(date=end_date)
            stats_list.append(stats)
            continue
        except Statistics.DoesNotExist:
            stats = Statistics(date=end_date)

            orders = Order.objects.filter(
                status='complete',
                type='sell',
                terminated_date__gt=start_date,
                terminated_date__lte=end_date).order_by(
                '-terminated_date').exclude(
                associated__membership=True).exclude(
                company__membership=True)

            if not orders:
                stats_list.append(stats)
                continue

            costs = Cost.objects.filter(date__gt=start_date,
                                        date__lte=end_date).order_by("-date")

            pending_payments = PendingPayment.objects.filter(
                created_date__gt=start_date,
                created_date__lte=end_date).order_by("-created_date")

            context = computeReport(orders, costs, pending_payments)

            stats.completed_orders = len(orders)
            stats.gross_income = context['total']['gross']
            stats.profit_before_costs = context['total']['net']
            stats.labor_income = context['orders'].labor
            stats.discount = context['total']['discount']
            stats.third_party = context['total']['third_party']
            stats.supplies = context['total']['consumable']
            stats.costs = context['costs'].total
            stats.parts_cost = context['parts_cost']
            stats.parts_price = context['parts_price']
            stats.payment_amount = context['payment_total']
            stats.transactions = context['payment_transactions']
            stats.debt_paid = context['debt_paid']

            stats.debt_created = 0
            for cat in context['payment_cats']:
                if cat.name == "debt":
                    stats.debt_created = cat.amount
                    break

            # Membership stats

            orders = Order.objects.filter(
                status='complete',
                type='sell',
                terminated_date__gt=start_date,
                terminated_date__lte=end_date).order_by(
                '-terminated_date').exclude(
                company__membership=False).exclude(
                company=None)

            context = computeReport(orders, costs, pending_payments)

            stats.membership_orders = len(context['orders'])
            stats.membership_amount = context['total']['net']

            stats.save()
            stats_list.append(stats)

    return stats_list
