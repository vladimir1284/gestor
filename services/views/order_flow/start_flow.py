from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def select_order_flow(request):
    return render(request, "services/order_flow.html")
