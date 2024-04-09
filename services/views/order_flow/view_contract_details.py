from datetime import datetime
from datetime import timedelta

import pytz
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from rent.models.lease import Contract
from rent.models.lease import Lease
from rent.models.vehicle import TrailerPicture
from rent.tools.client import compute_client_debt
from services.models import Order
from services.models.preorder import Preorder
from services.models.preorder_data import PreorderData
from services.tools.order import getRepairDebt
from services.views.category import get_object_or_404
from users.models import Company


@login_required
def view_contract_details(request, id):
    contract: Contract = get_object_or_404(Contract, id=id)

    if request.method == "POST":
        towit, _ = Company.objects.get_or_create(
            name="Towithouston",
            defaults={"name": "Towithouston"},
        )
        preorder_data = PreorderData.objects.filter(
            associated=contract.lessee,
        ).last()
        if preorder_data is None:
            preorder_data = PreorderData.objects.create(
                associated=contract.lessee,
            )

        preorder: Preorder = Preorder(
            preorder_data=preorder_data,
            trailer=contract.trailer,
            company=towit,
        )
        preorder.save()
        return redirect("create-service-order", preorder.id)

    effective_time = contract.effective_date.today() - contract.effective_date

    leases = Lease.objects.filter(contract=contract)
    lease = leases[0]
    debs, last_paid, unpaid = compute_client_debt(lease)

    rental_debt = -1
    rental_last_payment = None
    if debs > 0:
        rental_debt = debs
        rental_last_payment = unpaid[0].start

    repair_debt, repair_overdue, repair_weekly_payment = getRepairDebt(
        contract.lessee)

    last_order = (
        Order.objects.filter(
            trailer=contract.trailer,
        )
        .order_by("created_date")
        .last()
    )
    if last_order is not None:
        effective_time = (
            last_order.created_date.now(timezone.utc) - last_order.created_date
        )
        if last_order.created_date < (
            datetime.now(pytz.timezone("UTC")) - timedelta(days=90)
        ):
            last_order = None

    images = TrailerPicture.objects.filter(trailer=contract.trailer)
    pinned_image = None
    for image in images:
        if image.pinned:
            pinned_image = image
            break

    context = {
        "contract": contract,
        "effective_time": effective_time.days,
        "rental_debt": rental_debt,
        "rental_last_payment": rental_last_payment,
        "repair_debt": repair_debt,
        "repair_overdue": repair_overdue,
        "repair_last_payment": repair_weekly_payment,
        "last_order": last_order,
        "equipment": contract.trailer,
        "pinned_image": pinned_image,
    }
    return render(request, "services/view_contract_details.html", context)
