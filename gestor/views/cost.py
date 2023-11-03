from datetime import timedelta, date
from django.shortcuts import (
    render,
)
from django.contrib.auth.decorators import login_required
from costs.models import Cost

from gestor.views.utils import getWeek, getMonthYear


@login_required
def weekly_cost(request, category_id, date):

    (start_date, end_date, previousWeek, nextWeek) = getWeek(date)

    costs = Cost.objects.filter(
        category_id=category_id,
        date__range=(start_date, end_date)
    ).order_by("-date", "-id")

    return render(request, 'costs/cost_list.html', {'costs': costs})


@login_required
def monthly_cost(request, category_id, year, month):

    ((previousMonth, previousYear),
        (currentMonth, currentYear),
        (nextMonth, nextYear)) = getMonthYear(month, year)

    start_date = date(currentYear, currentMonth, 1)
    end_date = date(nextYear, nextMonth, 1) - timedelta(days=1)

    if category_id == "-1":
        costs = Cost.objects.filter(
            category__isnull=True,
            date__range=(start_date, end_date)
        ).order_by("-date")
    else:
        costs = Cost.objects.filter(
            category_id=category_id,
            date__range=(start_date, end_date)
        ).order_by("-date")

    return render(request, 'costs/cost_list.html', {'costs': costs})
