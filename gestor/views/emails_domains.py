from django.http import HttpRequest
from django.http import JsonResponse

from gestor.tools.emails_domains import get_email_domains


def emails_domains(request: HttpRequest):
    domains = get_email_domains()
    return JsonResponse(domains, safe=False)
