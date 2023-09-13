from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from schedule.views import _api_occurrences
from schedule.models import Calendar
from datetime import datetime


@login_required
def api_occurrences(request):
    start = str(datetime.fromisoformat(request.GET.get("start")).timestamp())
    end = str(datetime.fromisoformat(request.GET.get("end")).timestamp())
    calendar_slug = request.GET.get("calendar_slug")
    timezone = request.GET.get("timezone")

    try:
        response_data = _api_occurrences(start, end, calendar_slug, timezone)
    except (ValueError, Calendar.DoesNotExist) as e:
        return HttpResponseBadRequest(e)

    return JsonResponse(response_data, safe=False)
