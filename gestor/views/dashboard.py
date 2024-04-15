from datetime import datetime
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from dashboard.dashboard.dashboard import DASHBOARD
from dashboard.tools.calculate_stats import calculate_stats
from utils.models import Statistics


@login_required
def dashboard(request):
    ctx = {
        "dashboard_cards": DASHBOARD,
    }

    if "403" in request.session and request.session["403"]:
        request.session["403"] = None
        ctx["e403"] = True

    return render(
        request,
        "dashboard.html",
        ctx,
    )


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
