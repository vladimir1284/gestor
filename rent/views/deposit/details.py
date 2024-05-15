from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rent.tools.deposit import trailer_deposit_context


@login_required
def trailer_deposit_details(request, id):
    context = trailer_deposit_context(request, id)
    return render(request, "rent/trailer_deposit_details.html", context)
