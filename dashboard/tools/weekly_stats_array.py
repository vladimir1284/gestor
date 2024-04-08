from typing import List

from dashboard.tools.calculate_stats import calculate_stats
from gestor.views.utils import getWeek
from utils.models import Statistics


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
