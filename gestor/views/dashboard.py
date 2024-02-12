import calendar
from datetime import datetime
from datetime import time
from datetime import timedelta
from typing import List

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from costs.models import Cost
from gestor.views.reports import computeReport
from gestor.views.utils import getMonthYear
from gestor.views.utils import getWeek
from inventory.models import Product
from inventory.models import ProductTransaction
from rent.models.lease import Contract
from rent.models.lease import Due
from rent.models.lease import Lease
from rent.models.lease import LeaseDeposit
from rent.models.lease import SecurityDepositDevolution
from rent.models.vehicle import Trailer
from rent.views.client import compute_client_debt
from rent.views.client import get_sorted_clients
from services.models import (
    PendingPayment,
)
from services.tools.order import computeOrderAmount
from users.views import get_debtor
from utils.models import MonthlyStatistics
from utils.models import Order
from utils.models import Statistics


@login_required
def dashboard(request):
    stats_list = weekly_stats_array(n=2)
    last_date = stats_list[0].date - timedelta(days=1)

    # Profit
    current_profit = stats_list[0].profit_before_costs - stats_list[0].costs
    previous_profit = stats_list[1].profit_before_costs - stats_list[1].costs
    profit_increment = 0
    if current_profit > 0:
        profit_increment = 100 * \
            (current_profit - previous_profit) / current_profit

    # Parts
    current_parts_profit = stats_list[0].parts_price - stats_list[0].parts_cost
    previous_parts_profit = stats_list[1].parts_price - \
        stats_list[1].parts_cost
    parts_profit_increment = 0
    if current_parts_profit > 0:
        parts_profit_increment = (
            100 * (current_parts_profit - previous_parts_profit) /
            current_parts_profit
        )

    # Costs
    current_costs = stats_list[0].costs
    previous_costs = stats_list[1].costs
    costs_increment = 0
    if current_costs > 0:
        costs_increment = 100 * \
            (current_costs - previous_costs) / current_costs

    # Debt balance
    current_debt_balance = stats_list[0].debt_created - stats_list[0].debt_paid
    previous_debt_balance = stats_list[1].debt_created - \
        stats_list[1].debt_paid
    debt_increment = 0
    if current_debt_balance > 0:
        debt_increment = (
            100 * (current_debt_balance - previous_debt_balance) /
            current_debt_balance
        )
    # Stock costs
    current_stock_cost = Product.objects.filter(active=True).aggregate(
        Sum("stock_price")
    )["stock_price__sum"]

    # Purchase orders
    purchase_orders = Order.objects.filter(
        status="complete",
        type="purchase",
        terminated_date__gt=stats_list[0].date,
        terminated_date__lte=stats_list[1].date,
    )
    # Stock costs added
    transactions = ProductTransaction.objects.filter(order__in=purchase_orders)
    added = 0
    for trans in transactions:
        added += trans.getAmount()

    stock_cost_increment = 0

    if not current_stock_cost:
        current_stock_cost = 0
    else:
        stock_cost_increment = (
            100 * (added - stats_list[0].parts_cost) / current_stock_cost
        )

    # Memebership
    current_membership = stats_list[0].membership_amount
    previous_membership = stats_list[1].membership_amount
    membership_increment = 0
    if current_membership > 0:
        membership_increment = (
            100 * (current_membership - previous_membership) /
            current_membership
        )

    # Time series
    stats_list = monthly_stats_array(n=6)
    stats_list.reverse()

    time_labels = [stats.date.strftime("%b") for stats in stats_list]
    # time_labels[0] = ""

    profit_data = [
        int(
            x.profit_before_costs
            - x.costs
            + x.security_payments
            - x.returned_security_payments
        )
        for x in stats_list
    ]

    parts_data = [int(x.parts_price - x.parts_cost) for x in stats_list]
    expenses_data = [int(x.costs) for x in stats_list]

    indicators = [
        {
            "name": "Profit",
            "amount": current_profit,
            "increment": profit_increment,
            "positive": profit_increment > 0,
            "series": profit_data,
            "icon": "assets/img/icons/profit.png",
        },
        {
            "name": "Parts",
            "amount": current_parts_profit,
            "increment": parts_profit_increment,
            "positive": parts_profit_increment > 0,
            "series": parts_data,
            "icon": "assets/img/icons/parts.jpg",
        },
        {
            "name": "Expenses",
            "amount": current_costs,
            "increment": costs_increment,
            "positive": costs_increment < 0,
            "series": expenses_data,
            "icon": "assets/img/icons/costs.png",
        },
        {
            "name": "Debt",
            "amount": current_debt_balance,
            "increment": debt_increment,
            "positive": debt_increment < 0,
            "series": None,
            "icon": "assets/img/icons/debt.png",
        },
        {
            "name": "Stock",
            "amount": current_stock_cost,
            "increment": stock_cost_increment,
            "positive": stock_cost_increment < 0,
            "series": None,
            "icon": "assets/img/icons/inventory.png",
        },
        {
            "name": "TOWIT",
            "amount": current_membership,
            "increment": membership_increment,
            "positive": membership_increment < 0,
            "series": None,
            "icon": "assets/img/icons/TOWIT.png",
        },
    ]

    # Rental
    clients_by_date, n_active, n_processing, n_ended, rental_debt = get_sorted_clients(
        n=5
    )
    (
        clients_by_amount,
        n_active,
        n_processing,
        n_ended,
        rental_debt,
    ) = get_sorted_clients(n=5, order_by="amount")

    # Get unpaid dues from yesterday
    yesterday_dues = []

    leases = Lease.objects.filter(contract__stage="active")

    # Get the first time of today
    first_time = datetime.combine(
        timezone.now().date(), time.min) - timedelta(days=1)
    # Get the last time of today
    last_time = datetime.combine(
        timezone.now().date(), time.max) - timedelta(days=1)
    for lease in leases:
        occurrences = (
            []
            if lease.event is None
            else lease.event.get_occurrences(first_time, last_time)
        )
        for occurrence in occurrences:
            paid_dues = Due.objects.filter(due_date=occurrence.start.date())
            if len(paid_dues) == 0:
                client = lease.contract.lessee
                (
                    client.debt,
                    client.last_payment,
                    client.unpaid_dues,
                ) = compute_client_debt(lease)
                if client.debt > 0:
                    client.last_payment = client.unpaid_dues[0].start
                yesterday_dues.append(client)
    # Trailers available
    active_contracts = Contract.objects.filter(stage__in=("active", "missing"))
    rented_ids = []
    for contract in active_contracts:
        rented_ids.append(contract.trailer.id)
    available = Trailer.objects.filter(active=True).exclude(id__in=rented_ids)

    orders_payment_pending = Order.objects.filter(
        type="sell", status="payment_pending"
    ).order_by("-created_date")

    for order in orders_payment_pending:
        computeOrderAmount(order)

    order_storage = Order.objects.filter(position=0)

    for o in order_storage:
        if o.trailer is None:
            trailer = Trailer()
            trailer.vin = o.vin
            trailer.plate = o.plate
            trailer.type = "Client's trailer"
            o.trailer = trailer

    context = {
        "indicators": indicators,
        "last_date": last_date,  # TODO fix this
        "time_labels": time_labels,
        "insights": stats_list[-1].gpt_insights,
        "rental_debt": rental_debt,
        "clients_by_date": clients_by_date,
        "clients_by_amount": clients_by_amount,
        "yesterday_dues": yesterday_dues,
        "available": available,
        "payment_pending": orders_payment_pending,
        "orders_storage": order_storage,
    }
    context = dict(context, **get_debtor(request))

    return render(request, "dashboard.html", context)


def monthly_stats_array(n=6) -> List[MonthlyStatistics]:
    """
    Compute monthly stats for a given date
    Returns a list for several month stats
    We get the data from the previous month
    """
    (
        (previousMonth, previousYear),
        (currentMonth, currentYear),
        (nextMonth, nextYear),
    ) = getMonthYear()  # This month
    stats_list = []
    for _ in range(n):
        # Previous month
        (
            (previousMonth, previousYear),
            (currentMonth, currentYear),
            (nextMonth, nextYear),
        ) = getMonthYear(previousMonth, previousYear)

        # monthly stats are stored in the end_date of the month
        start_date = datetime(currentYear, currentMonth, 1)
        _, last_day = calendar.monthrange(currentYear, currentMonth)
        last_date = datetime(currentYear, currentMonth, last_day)
        try:
            stats = MonthlyStatistics.objects.get(date=last_date)
            stats_list.append(stats)
            continue
        except MonthlyStatistics.DoesNotExist:
            stats = MonthlyStatistics(date=last_date)
            calculate_stats(stats, start_date, last_date)

            stats_list.append(stats)

    return stats_list


def weekly_stats_array(date=None, n=12) -> List[Statistics]:
    """
    Compute weekly stats for a given date
    Returns a list for several week stats
    We get the data from the previous week
    """

    (start_date, end_date, previousWeek, nextWeek) = getWeek(date)  # This week
    stats_list = []
    for _ in range(n):
        # Previous week
        (start_date, end_date, previousWeek, nextWeek) = getWeek(
            previousWeek.strftime("%m%d%Y")
        )

        try:
            # Weekly stats are stored in the end_date of the week
            stats = Statistics.objects.get(date=end_date)
            stats_list.append(stats)
            continue
        except Statistics.DoesNotExist:
            stats = Statistics(date=end_date)
            calculate_stats(stats, start_date, end_date)

            stats_list.append(stats)

    return stats_list


def week_stats_recalculate(request, date):
    """
    This function first converts the date parameter from a string format to a
    date object. Then, it calculates the start and end dates of the week based
    on the given date.
    Then, it calls the calculate_stats function to recalculate the statistics
    for the week, using the start and end dates.
    Finally, it redirects the user to the "dashboard" page.
    """

    # Obtiene las fechas de la semana
    date = datetime.strptime(date, "%m%d%Y").date()
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=7)

    # Calcula las estadísticas de la semana
    stats = get_object_or_404(Statistics, date=end_date)

    calculate_stats(stats, start_date, end_date)

    # Renderiza la plantilla
    return redirect("dashboard")


def calculate_stats(stats, start_date, end_date):
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
    )

    costs = Cost.objects.filter(date__range=(
        start_date, end_date)).order_by("-date")

    pending_payments = PendingPayment.objects.filter(
        created_date__gt=start_date, created_date__lte=end_date
    ).order_by("-created_date")

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
