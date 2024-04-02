import calendar
from datetime import datetime
from typing import List

from dashboard.tools.calculate_stats import calculate_stats
from gestor.views.utils import getMonthYear
from utils.models import MonthlyStatistics


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
