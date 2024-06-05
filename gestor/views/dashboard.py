from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from dashboard.dashboard.dashboard import DASHBOARD
from gestor.tools.week_stats_recal import week_stats_recal


@login_required
def dashboard(request):
    ctx = {
        "dashboard_cards": DASHBOARD,
    }

    if "403" in request.session and request.session["403"]:
        request.session["403"] = None
        ctx["e403"] = True

    if "js" in request.session and request.session["js"]:
        ctx["js"] = request.session["js"]
        request.session["js"] = None

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
    week_stats_recal(date)

    # Renderiza la plantilla
    return redirect("dashboard")
