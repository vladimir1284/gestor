from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from inventory.models import Product, Associated


@login_required
def dashboard(request):
    total_product = Product.objects.count()
    total_associated = Associated.objects.count()
    context = {
        'product': total_product,
        'associated': total_associated,
    }
    return render(request, 'dashboard.html', context)
