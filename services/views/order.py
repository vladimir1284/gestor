from django.db.models import Q
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
from services.tools.conditios_to_pdf import (
    conditions_to_pdf,
    send_pdf_conditions_to_email,
)
from services.tools.order import getRepairDebt, getOrderContext, computeOrderAmount
from django.http import HttpResponse

from services.tools.trailer_identification_to_pdf import trailer_identification_to_pdf
from services.views.invoice import get_invoice_context, sendMail


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
    Order,
    ServicePicture,
    Payment,
)
from services.forms import (
    DiscountForm,
    OrderCreateForm,
    OrderEndUpdatePositionForm,
    OrderSignatureForm,
    OrderVinPlateForm,
)
from rent.models.vehicle import Trailer, TrailerPicture
from django.utils.translation import gettext_lazy as _
from gestor.views.utils import getMonthYear
from datetime import datetime, timedelta

# -------------------- Order ----------------------------


@login_required
def create_order(request):
    client_id = request.session.get("client_id")
    client = None
    if client_id:
        client = Associated.objects.get(id=client_id)

    if request.session["using_signature"] and request.session["signature"] is None:
        orders = Order.objects.filter(associated=client)
        if len(orders) == 0:
            return redirect("view-conditions")

    initial = {"concept": "Maintenance to trailer"}
    creating_order = request.session.get("creating_order")
    request.session["all_selected"] = True
    order = Order()
    if creating_order:
        if client:
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

    getPlate = request.session["plate"]
    form = OrderCreateForm(initial=initial, get_plate=order.external)
    if request.method == "POST":
        form = OrderCreateForm(request.POST, get_plate=getPlate)
        form.clean()
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

            if order.associated is not None and order.associated.email is not None:
                send_pdf_conditions_to_email(
                    request, order.id, [order.associated.email]
                )

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
    request.session["plate"] = False
    request.session["signature"] = None
    request.session["using_signature"] = False
    request.session["next"] = None


@login_required
def update_order(request, id):
    # fetch the object related to passed id
    order = get_object_or_404(Order, id=id)

    form = OrderCreateForm(instance=order, get_plate=order.external)

    if request.method == "POST":
        # pass the object as instance in form
        form = OrderCreateForm(request.POST, instance=order, get_plate=order.external)

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
            return redirect("update-order-position", id, status)

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

    if status == "decline":
        return redirect("update-order-position", id, status)
    return redirect("list-service-order")


@login_required
def order_end_update_position(request, id, status):
    order = get_object_or_404(Order, id=id)
    if status == "decline":
        order.position = None
        order.save()
        return redirect("list-service-order")

    if status == "complete" and order.position is None:
        return redirect("process-payment", id)

    old_status = order.status
    order.status = status
    if request.method == "POST":
        form = OrderEndUpdatePositionForm(request.POST, order=order)
        if form.is_valid():
            order.status = old_status
            pos = form.cleaned_data["position"]
            if pos == "":
                pos = None
            order.position = pos
            order.save()
            if status == "complete":
                return redirect("process-payment", id)
            return redirect("list-service-order")
    else:
        form = OrderEndUpdatePositionForm(order=order)

    context = {
        "form": form,
        "title": "Select position",
    }
    return render(request, "services/order_end_update_position.html", context)


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
        request, ("complete", "decline", "payment_pending"), currentYear, currentMonth
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
    orders = sorted(orders, key=lambda x: 0 if x.status == "payment_pending" else 1)

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

    orders = sorted(orders, key=lambda x: 0 if x.status == "payment_pending" else 1)

    # orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        # transactions = ProductTransaction.objects.filter(order=order)
        computeOrderAmount(order)
    return {"orders": orders, "statuses": statuses}


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

    order = context["order"]
    client = order.associated
    if client is not None:
        orders = Order.objects.filter(
            ~Q(id=1),
            associated=client,
            created_date__lt=order.created_date,
        ).order_by("-created_date")
        for order in orders:
            computeOrderAmount(order)
        context.setdefault("history", orders)

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
    request.session["plate"] = True
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

    client = None
    if request.session["client_id"]:
        client = Associated.objects.get(id=request.session["client_id"])

    HasOrders = False
    if client is not None:
        orders = Order.objects.filter(associated=client)
        HasOrders = len(orders) > 0

    context = {
        "signature": signature,
        "client": client,
        "hasOrder": HasOrders,
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
        Order.objects.filter(trailer=contract.trailer).order_by("created_date").last()
    )
    if last_order is not None:
        effective_time = (
            last_order.created_date.now(timezone.utc) - last_order.created_date
        )
        if last_order.created_date < (
            datetime.now(pytz.timezone("UTC")) - timedelta(days=90)
        ):
            last_order = None

    towit, created = Company.objects.get_or_create(
        name="Towithouston", defaults={"name": "Towithouston"}
    )
    request.session["client_id"] = contract.lessee.id
    request.session["trailer_id"] = contract.trailer.id
    request.session["company_id"] = towit.id

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


##### PDF #####
@login_required
def show_conditions_as_pdf(request, id):
    result = conditions_to_pdf(request, id)
    if result is not None:
        response = HttpResponse(content_type="application/pdf;")
        response["Content-Disposition"] = "inline; filename=invoice_towit.pdf"
        response["Content-Transfer-Encoding"] = "binary"
        with tempfile.NamedTemporaryFile() as output:
            output.write(result)
            output.flush()
            output = open(output.name, "rb")
            response.write(output.read())
        return response

    return None


@login_required
def gen_trailer_indentification_pdf(request, id):
    result = trailer_identification_to_pdf(request, id)
    if result is not None:
        response = HttpResponse(content_type="application/pdf;")
        response["Content-Disposition"] = "inline; filename=invoice_towit.pdf"
        response["Content-Transfer-Encoding"] = "binary"
        with tempfile.NamedTemporaryFile() as output:
            output.write(result)
            output.flush()
            output = open(output.name, "rb")
            response.write(output.read())
        return response
    return None


@login_required
def send_invoice_email(request, id):
    context = get_invoice_context(id)
    order = context["order"]

    if order is None:
        return redirect("detail-service-order", id)

    mail_address = ""
    if order.associated and order.associated.email:
        mail_address = order.associated.email
    elif order.company and order.company.email:
        mail_address = order.company.email

    sendMail(context, request, mail_address, False)

    order.invoice_sended = True
    order.save()

    return redirect("detail-service-order", id)
