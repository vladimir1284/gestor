from django.db.models import Sum

from dashboard.tools.monthly_stats_array import monthly_stats_array
from dashboard.tools.weekly_stats_array import weekly_stats_array
from inventory.models import Product
from inventory.models import ProductTransaction
from utils.models import Order


def get_indicators():
    stats_list = weekly_stats_array(n=2)

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

    return [
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
