from django.conf import settings
from django.shortcuts import redirect


def process_ended_page(request):
    return redirect(settings.REDIR_CLIENTS)
    # context = {
    #     "redir_client": settings.REDIR_CLIENTS,
    # }
    # return render(request, "services/process_ended.html", context)
