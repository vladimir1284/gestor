from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import pytz
import re
import base64
import tempfile
from rent.models.lease import Contract, Lease
from rent.tools.client import compute_client_debt
from services.tools.order import getRepairDebt


from .sms import twilioSendSMS
from .transaction import reverse_transaction
from users.models import (
    Associated,
    Company,
)
from inventory.models import (
    ProductTransaction,
)
from inventory.views.transaction import (
    NotEnoughStockError,
)
from services.models import (
    OrderSignature,
    ServiceTransaction,
    Order,
    Expense,
    ServicePicture,
    Payment,
    DebtStatus,
)
from services.forms import (
    DiscountForm,
    OrderCreateForm,
    OrderSignatureForm,
    OrderVinPlateForm,
)
from rent.models.vehicle import Trailer
from django.utils.translation import gettext_lazy as _
from gestor.views.utils import getMonthYear
from datetime import datetime, timedelta

# -------------------- Order ----------------------------


@login_required
def create_order(request):
    if request.session["using_signature"] and request.session["signature"] is None:
        return redirect("view-conditions")

    initial = {"concept": None}
    creating_order = request.session.get("creating_order")
    request.session["all_selected"] = True
    order = Order()
    if creating_order:
        client_id = request.session.get("client_id")
        if client_id:
            client = Associated.objects.get(id=client_id)
            order.associated = client

        company_id = request.session.get("company_id")
        if company_id:
            company = Company.objects.get(id=company_id)
            order.company = company

        trailer_id = request.session.get("trailer_id")
        if trailer_id:
            trailer = Trailer.objects.get(id=trailer_id)
            initial = {"concept": _("Maintenance to trailer")}
            order.trailer = trailer

        VIN = request.session.get("VIN")
        if VIN:
            order.vin = VIN
            initial["vin"] = VIN

        Plate = request.session.get("Plate")
        if Plate:
            order.plate = Plate

    form = OrderCreateForm(initial=initial)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.type = "sell"
            order.created_by = request.user

            # Link the client to order
            client_id = request.session.get("client_id")
            if client_id:
                client = Associated.objects.get(id=client_id)
                order.associated = client

            # Set the equipment type in the order
            equipment_type = request.session.get("equipment_type")
            if equipment_type:
                order.equipment_type = equipment_type

            # Link trailer to order if exists
            trailer_id = request.session.get("trailer_id")
            if trailer_id:
                trailer = Trailer.objects.get(id=trailer_id)
                order.trailer = trailer

            # Link company to order if exists
            company_id = request.session.get("company_id")
            if company_id:
                company = Company.objects.get(id=company_id)
                order.company = company

            order.save()
            if (
                "signature" in request.session
                and request.session["signature"] is not None
            ):
                signature = OrderSignature.objects.get(id=request.session["signature"])
                signature.order = order
                signature.save()
            cleanSession(request)

            return redirect("detail-service-order", id=order.id)

    context = {
        "form": form,
        "title": _("Create service order"),
        "order": order,
    }
    return render(request, "services/order_create.html", context)


def cleanSession(request):
    request.session["creating_order"] = None
    request.session["client_id"] = None
    request.session["vehicle_id"] = None
    request.session["trailer_id"] = None
    request.session["company_id"] = None
    request.session["all_selected"] = None
    request.session["order_detail"] = None
    request.session["equipment_type"] = None
    request.session["VIN"] = None
    request.session["Plate"] = None
    request.session["signature"] = None
    request.session["using_signature"] = False
    request.session["next"] = None


@login_required
def update_order(request, id):
    # fetch the object related to passed id
    order = get_object_or_404(Order, id=id)

    form = OrderCreateForm(instance=order)

    if request.method == "POST":
        # pass the object as instance in form
        form = OrderCreateForm(request.POST, instance=order)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            return redirect("detail-service-order", id)

    # add form dictionary to context
    context = {"form": form, "order": order, "title": _("Update service order")}

    return render(request, "services/order_create.html", context)


@login_required
def update_order_status(request, id, status):
    order = get_object_or_404(Order, id=id)

    try:
        if status == "complete":
            return redirect("process-payment", id)

        elif order.status == "complete":
            if status == "decline":
                # Reverse stock
                transactions = ProductTransaction.objects.filter(order=order)
                for transaction in transactions:
                    reverse_transaction(transaction)

        if order.status == "pending":
            if status == "processing" and (not order.company and not order.associated):
                return redirect(
                    "detail-service-order", id, "Please add a client or a company"
                )

        if status == "processing":
            # Send SMS
            order.processing_date = timezone.localtime(timezone.now())
            twilioSendSMS(order, status)

        order.status = status
        order.save()
    except NotEnoughStockError as error:
        print(error)
    return redirect("list-service-order")


STATUS_ORDER = ["pending", "processing", "approved", "complete", "decline"]


@login_required
def list_order(request):
    context = prepareListOrder(request, ("processing", "pending"))
    context.setdefault("stage", "Terminated")
    context.setdefault("alternative_view", "list-service-order-terminated")
    return render(request, "services/order_list.html", context)


@login_required
def list_terminated_order(request, year=None, month=None):
    (
        (previousMonth, previousYear),
        (currentMonth, currentYear),
        (nextMonth, nextYear),
    ) = getMonthYear(month, year)

    context = preparePaginatedListOrder(
        request, ("complete", "decline"), currentYear, currentMonth
    )
    context.setdefault("stage", "Active")
    context.setdefault("alternative_view", "list-service-order")

    context.setdefault("previousMonth", previousMonth)
    context.setdefault("currentMonth", currentMonth)
    context.setdefault("nextMonth", nextMonth)
    context.setdefault("thisMonth", datetime.now().month)
    context.setdefault("previousYear", previousYear)
    context.setdefault("currentYear", currentYear)
    context.setdefault("nextYear", nextYear)
    context.setdefault("thisYear", datetime.now().year)
    context.setdefault("interval", "monthly")
    return render(request, "services/order_list.html", context)


def prepareListOrder(request, status_list):
    # Prepare the flow for creating order
    cleanSession(request)
    request.session["creating_order"] = True

    # List orders
    orders = Order.objects.filter(type="sell", status__in=status_list).order_by(
        "-created_date"
    )
    # orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        # transactions = ProductTransaction.objects.filter(order=order)
        computeOrderAmount(order)
    return {"orders": orders, "statuses": statuses}


def preparePaginatedListOrder(request, status_list, currentYear, currentMonth):
    # Prepare the flow for creating order
    cleanSession(request)
    request.session["creating_order"] = True

    # List orders
    orders = Order.objects.filter(
        type="sell",
        status__in=status_list,
        created_date__year=currentYear,
        created_date__month=currentMonth,
    ).order_by("-created_date")

    # orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        # transactions = ProductTransaction.objects.filter(order=order)
        computeOrderAmount(order)
    return {"orders": orders, "statuses": statuses}


def computeOrderAmount(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    transactions.satisfied = True
    services = ServiceTransaction.objects.filter(order=order)
    expenses = Expense.objects.filter(order=order)
    # Compute amount
    amount = 0
    tax = 0
    for transaction in transactions:
        transaction.satisfied = transaction.product.computeAvailable() >= 0
        if not transaction.satisfied:
            transactions.satisfied = False

        transaction.amount = transaction.getAmount()
        amount += transaction.amount
        transaction.total_tax = transaction.getTax()
        tax += transaction.total_tax
    for service in services:
        service.amount = service.getAmount()
        amount += service.amount
        service.total_tax = service.getTax()
        tax += service.total_tax
    expenses.amount = 0
    for expense in expenses:
        expenses.amount += expense.cost
    amount += expenses.amount
    order.amount = amount
    order.tax = tax
    return (transactions, services, expenses)


def getOrderContext(order_id):
    order = Order.objects.get(id=order_id)
    (transactions, services, expenses) = computeOrderAmount(order)
    satisfied = transactions.satisfied
    # Order by amount
    transactions = list(transactions)
    # Costs
    parts_cost = 0
    consumable_cost = 0
    # Count consumables and parts
    consumable_amount = 0
    parts_amount = 0
    consumable_tax = 0
    parts_tax = 0
    consumables = False

    for trans in transactions:
        if trans.product.type == "part":
            parts_amount += trans.amount
            parts_tax += trans.total_tax
            parts_cost += trans.getMinCost()
        elif trans.product.type == "consumable":
            consumables = True
            consumable_amount += trans.amount
            consumable_tax += trans.total_tax
            if trans.cost is not None:
                consumable_cost += trans.cost
    # Account services
    service_amount = 0
    service_tax = 0
    for service in services:
        service_amount += service.amount
        service_tax += service.total_tax
    # Terminated order
    terminated = order.status in ["decline", "complete"]
    empty = (len(services) + len(transactions)) == 0
    # Compute totals
    order.total = order.amount + order.tax - order.discount
    consumable_total = consumable_tax + consumable_amount
    parts_total = parts_amount + parts_tax
    service_total = service_amount + service_tax
    # Compute tax percent
    tax_percent = 8.25

    # Profit
    profit = order.amount - expenses.amount - consumable_cost - parts_cost

    if order.associated:
        if order.associated.debt > 0:
            order.associated.debt_status = DebtStatus.objects.filter(
                client=order.associated
            )[0].status
    try:
        order.associated.phone_number = order.associated.phone_number.as_national
    except:
        pass
    return {
        "order": order,
        "services": services,
        "satisfied": satisfied,
        "service_amount": service_amount,
        "service_total": service_total,
        "service_tax": service_tax,
        "expenses": expenses,
        "expenses_amount": expenses.amount,
        "transactions": transactions,
        "consumable_amount": consumable_amount,
        "consumable_total": consumable_total,
        "consumable_tax": consumable_tax,
        "parts_amount": parts_amount,
        "parts_total": parts_total,
        "parts_tax": parts_tax,
        "terminated": terminated,
        "empty": empty,
        "tax_percent": tax_percent,
        "consumables": consumables,
        "profit": profit,
    }


@login_required
def detail_order(request, id, msg=None):
    # Prepare the flow for creating order
    request.session["creating_order"] = None
    request.session["order_detail"] = id

    # Get data for the given order
    context = getOrderContext(id)
    if msg or msg != "":
        context["mensaje"] = msg

    # Discount
    if request.method == "POST":
        form = DiscountForm(
            request.POST, total=context["order"].total, profit=123.4357239847
        )
        if form.is_valid():
            # Restore the old discount
            context["order"].total += context["order"].discount
            context["order"].discount = (
                context["order"].total - form.cleaned_data["round_to"]
            )  # Compute the new discount
            # Apply the new discount
            context["order"].total -= context["order"].discount
            context["order"].save()

    form = DiscountForm(total=context["order"].total, profit=context["profit"])

    context.setdefault("form", form)

    # Pictures
    images = ServicePicture.objects.filter(order=context["order"])
    context.setdefault("images", images)

    if context["terminated"]:
        # Payments
        context.setdefault("payments", Payment.objects.filter(order=context["order"]))

    return render(request, "services/order_detail.html", context)


# Crating order: Select order's flow
@login_required
def select_order_flow(request):
    cleanSession(request)
    request.session["creating_order"] = True
    return render(request, "services/order_flow.html")


# Flow: client owns trailer
@login_required
def select_client(request):
    request.session["next"] = "view-conditions"
    request.session["using_signature"] = True
    if request.method == "POST":
        client = get_object_or_404(Associated, id=request.POST.get("id"))
        request.session["client_id"] = client.id
        # Redirect acording to the  corresponding flow
        if request.session.get("creating_order") is not None:
            return redirect("view-conditions")
        else:
            order_id = request.session.get("order_detail")
            if order_id is not None:
                order = get_object_or_404(Order, id=order_id)
                order.associated = client
                order.save()
                return redirect("detail-service-order", id=order_id)

    # add form dictionary to context
    associates = Associated.objects.filter(type="client", active=True).order_by(
        "name", "alias"
    )
    context = {"associates": associates, "skip": True}
    order_id = request.session.get("order_detail")
    if order_id is not None:
        context["skip"] = False
    return render(request, "services/client_list.html", context)


@login_required
def get_vin_plate(request):
    if request.session["using_signature"] and request.session["signature"] is None:
        return redirect("view-conditions")

    if request.method == "POST":
        form = OrderVinPlateForm(request.POST)
        if form.is_valid():
            vin = form.cleaned_data["VIN"]
            plate = form.cleaned_data["Plate"]
            if vin != "":
                request.session["VIN"] = vin
            if plate != "":
                request.session["Plate"] = plate
            return redirect("create-service-order")

    form = OrderVinPlateForm()
    context = {
        "form": form,
        "title": _("Insert trailer's VIN or Plate"),
    }
    return render(request, "services/order_vin_plate.html", context)


@login_required
def view_conditions(request):
    if "signature" in request.session and request.session["signature"] is not None:
        signature = OrderSignature.objects.get(id=request.session["signature"])
    else:
        signature = OrderSignature()
    context = {
        "signature": signature,
    }
    return render(request, "services/view_conditions.html", context)


@login_required
def create_handwriting(request):
    if request.method == "POST":
        form = OrderSignatureForm(request.POST, request.FILES)
        if form.is_valid():
            client_id = request.session["client_id"]
            associated = get_object_or_404(Associated, id=client_id)
            handwriting: OrderSignature = form.save(commit=False)
            handwriting.associated = associated
            handwriting.position = "signature_order_client"

            # Save image
            datauri = str(form.instance.img)
            image_data = re.sub("^data:image/png;base64,", "", datauri)
            image_data = base64.b64decode(image_data)
            with tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, prefix="firma_"
            ) as output:
                output.write(image_data)
                output.flush()
                name = output.name.split("/")[-1]
                with open(output.name, "rb") as temp_file:
                    form.instance.img.save(name, temp_file, True)

            handwriting.save()
            request.session["signature"] = handwriting.id
            return redirect("view-conditions")
    else:
        form = OrderSignatureForm()

    context = {
        "position": "signature",
        "form": form,
    }
    return render(request, "services/signature.html", context)


# Flow: client rent trailer
@login_required
def select_lessee(request):
    if request.method == "POST":
        client_id = request.POST.get("id")
        return redirect("select-service-lessee-trailer", id=client_id)

    contracts = Contract.objects.filter(stage="active").order_by(
        "lessee__name", "lessee__alias"
    )
    clients = []
    for contract in contracts:
        client = contract.lessee
        if client not in clients:
            clients.append(client)
    context = {
        "associates": clients,
        # "trailer_id": trailer_id,
        "create": False,
    }
    return render(request, "services/select_lessee.html", context)


@login_required
def select_lessee_trailer(request, id):
    if request.method == "POST":
        trailer_id = request.POST.get("id")
        contract = Contract.objects.get(
            stage="active", lessee__id=id, trailer__id=trailer_id
        )
        return redirect("view-contract-details", id=contract.id)

    contracts = Contract.objects.filter(stage="active", lessee__id=id)
    if len(contracts) == 1:
        return redirect("view-contract-details", id=contracts[0].id)

    trailers = []
    for contract in contracts:
        if contract.trailer not in trailers:
            trailers.append(contract.trailer)
    context = {
        "trailers": trailers,
    }
    return render(request, "services/select_trailer.html", context)


@login_required
def view_contract_details(request, id):
    contract = Contract.objects.get(id=id)

    effective_time = contract.effective_date.today() - contract.effective_date

    True if contract.tolldue_set.all().filter(stage="unpaid") else False

    leases = Lease.objects.filter(contract=contract)
    lease = leases[0]
    debs, last_paid, unpaid = compute_client_debt(lease)

    rental_debt = -1
    rental_last_payment = None
    if debs > 0:
        rental_debt = debs
        rental_last_payment = unpaid[0].start

    repair_debt, repair_overdue, repair_weekly_payment = getRepairDebt(contract.lessee)

    last_order = (
        Order.objects.filter(associated=contract.lessee).order_by("created_date").last()
    )
    if last_order is not None and last_order.created_date < (
        datetime.now(pytz.timezone("UTC")) - timedelta(days=90)
    ):
        last_order = None

    towit, created = Company.objects.get_or_create(
        name="Towithouston", defaults={"name": "Towithouston"}
    )
    request.session["client_id"] = contract.lessee.id
    request.session["trailer_id"] = contract.trailer.id
    request.session["company_id"] = towit.id

    context = {
        "contract": contract,
        "effective_time": effective_time,
        "rental_debt": rental_debt,
        "rental_last_payment": rental_last_payment,
        "repair_debt": repair_debt,
        "repair_overdue": repair_overdue,
        "repair_last_payment": repair_weekly_payment,
        "last_order": last_order,
    }
    return render(request, "services/view_contract_details.html", context)


# Flow: trailer without client
@login_required
def select_unrented_trailer(request):
    if request.method == "POST":
        trailer_id = request.POST.get("id")
        towit, created = Company.objects.get_or_create(
            name="Towithouston",
            defaults={"name": "Towithouston"},
        )
        request.session["trailer_id"] = trailer_id
        request.session["company_id"] = towit.id
        return redirect("create-service-order")

    unrented_trailers = []
    trailers = Trailer.objects.filter(active=True)
    for trailer in trailers:
        # Contracts
        has_contract = (
            Contract.objects.filter(trailer=trailer).exclude(stage="ended").exists()
        )
        if not has_contract:
            unrented_trailers.append(trailer)

    context = {
        "trailers": unrented_trailers,
    }
    return render(request, "services/select_trailer.html", context)
