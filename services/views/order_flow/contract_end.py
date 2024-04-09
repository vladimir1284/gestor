from django.shortcuts import render


def process_ended_page(request):
    context = {}
    return render(request, "services/process_ended.html", context)
