from django.conf import settings
from django.shortcuts import render


def process_ended_page(request):
    context = {
        "redir_client": settings.REDIR_CLIENTS,
    }
    print(context)
    return render(request, "services/process_ended.html", context)
