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
    stats_dates = [
        {
            "start": start_date,
            "end": end_date,
        }
    ]
    for _ in range(n):
        # Previous week
        (start_date, end_date, previousWeek, nextWeek) = getWeek(
            previousWeek.strftime("%m%d%Y")
        )
        stats_dates.append(
            {
                "start": start_date,
                "end": end_date,
            }
        )

    stats_list = Statistics.objects.filter(date__in=[d["end"] for d in stats_dates])
    existing_stats_dates = [s.date for s in stats_list]
    for date in stats_dates:
        if date["end"] not in existing_stats_dates:
            stats = Statistics(date=date["end"])
            calculate_stats(stats, date["start"], date["end"])
            stats_list.append(stats)

    return stats_list
