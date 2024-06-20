from datetime import timedelta

from django.db.models import Sum

from dashboard.dashboard.dashboard_card import DashboardCard
from dashboard.tools.get_indicators import get_indicators
from dashboard.tools.monthly_stats_array import monthly_stats_array
from dashboard.tools.weekly_stats_array import weekly_stats_array
from inventory.models import Product, ProductTransaction
from rbac.tools.permission_param import PermissionParam
from utils.models import Order


def _resolver():
    print("business insights")
    stats_list = weekly_stats_array(n=2)
    last_date = stats_list[0].date - timedelta(days=1)

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

    if not current_stock_cost:
        current_stock_cost = 0

    # Time series
    stats_list = monthly_stats_array(n=6)
    stats_list.reverse()

    time_labels = [stats.date.strftime("%b") for stats in stats_list]

    return {
        "last_date": last_date,  # TODO fix this
        "time_labels": time_labels,
        "insights": stats_list[-1].gpt_insights,
        "indicators": get_indicators(),
    }


def BusinessInsightsCard():
    return DashboardCard(
        name="Business Insights",
        template="dashboard/business_insights.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
