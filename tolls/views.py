from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import reverse

from .forms import TollCreateForm
from .forms import TollUpdateForm
from .models import TollDue
from gestor.views.utils import getMonthYear
from rent.models.lease import Contract
from rent.models.vehicle import TrailerPlates


@login_required
def create_toll(request, plate=None, contract=None):
    if not plate:
        context = {"plates": TrailerPlates.objects.all()}
        return render(request, "tolls/plates_list.html", context)
    elif not contract:
        _plate = TrailerPlates.objects.get(id=plate)
        context = {
            "contracts": Contract.objects.all().filter(trailer=_plate.trailer),
            "plate": _plate,
        }
        return render(request, "tolls/contracts_list.html", context)
    _plate = TrailerPlates.objects.get(id=plate)
    _contract = Contract.objects.get(id=contract)
    next_id = request.GET.get("next_id", None)
    form = TollCreateForm(plate=_plate, contract=_contract)
    if request.method == "POST":
        form = TollCreateForm(
            request.POST, request.FILES, plate=_plate, contract=_contract
        )
        if form.is_valid():
            form.save()
            if next_id:
                return redirect(reverse("list-toll") + f"{next_id}")
            else:
                return redirect("list-toll")

    context = {"form": form, "title": "Create Toll"}

    return render(request, "tolls/toll_create.html", context)


@login_required
def create_contract_toll(request, contract: int):
    _contract = Contract.objects.get(id=contract)
    _plate = TrailerPlates.objects.get(trailer=_contract.trailer)

    if request.method == "POST":
        form = TollCreateForm(
            request.POST, request.FILES, plate=_plate, contract=_contract
        )
        if form.is_valid():
            form.save()
            return redirect("ended-contract-details", contract)
    else:
        form = TollCreateForm(plate=_plate, contract=_contract)

    context = {"form": form, "title": "Create Contract Toll"}

    return render(request, "tolls/toll_create.html", context)


@login_required
def list_toll(request, id=None):

    year = request.GET.get("year", None)
    month = request.GET.get("month", None)

    (
        (previousMonth, previousYear),
        (currentMonth, currentYear),
        (nextMonth, nextYear),
    ) = getMonthYear(month, year)

    if not id:
        tolls = TollDue.objects.all().order_by("-created_date", "-id")
        tolls = tolls.filter(
            created_date__year=currentYear, created_date__month=currentMonth
        )
    else:
        tolls = TollDue.objects.all().filter(contract=id).order_by("-created_date")

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date is not None:
        tolls = tolls.filter(created_date__gte=start_date)

    if end_date is not None:
        tolls = tolls.filter(created_date__lte=end_date)

    contract = None

    if id:
        previousMonth = None
        previousYear = None
        _contract = Contract.objects.all().filter(id=id)
        if _contract:
            contract = _contract[0]

    context = {
        "previousMonth": previousMonth,
        "currentMonth": currentMonth,
        "nextMonth": nextMonth,
        "thisMonth": datetime.now().month,
        "previousYear": previousYear,
        "currentYear": currentYear,
        "nextYear": nextYear,
        "thisYear": datetime.now().year,
        "interval": "monthly",
        "tolls": tolls,
        "id": id,
        "contract": contract,
    }
    return render(request, "tolls/toll_list.html", context)


@login_required
def update_toll(request, id):
    toll = get_object_or_404(TollDue, id=id)
    form = TollUpdateForm(instance=toll, plate=toll.plate)
    next_id = request.GET.get("next_id", None)

    print("toll", toll.contract.id, toll.contract.tolldue_set.all())

    if request.method == "POST":
        form = TollUpdateForm(
            request.POST, request.FILES, instance=toll, plate=toll.plate
        )
        if form.is_valid():
            form.save()
            if next_id:
                return redirect(reverse("list-toll") + f"{next_id}")
            else:
                return redirect("list-toll")

    context = {"title": "Update toll", "form": form, "next_id": next_id}

    return render(request, "tolls/toll_create.html", context)


@login_required
def delete_toll(request, id):
    toll = get_object_or_404(TollDue, id=id)
    next_id = request.GET.get("next_id", None)
    toll.delete()
    if next_id:
        return redirect(reverse("list-toll") + f"{next_id}")
    else:
        return redirect("list-toll")

