import tempfile
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .sms import twilioSendSMS
from .transaction import reverse_transaction
from gestor.views.utils import getMonthYear
from inventory.models import (
    ProductTransaction,
)
from inventory.views.transaction import (
    NotEnoughStockError,
)
from services.forms import DiscountForm
from services.forms import OrderCreateForm
from services.forms import OrderDeclineReazon
from services.models import Order
from services.models import Payment
from services.models import ServicePicture
from services.tools.conditios_to_pdf import (
    conditions_to_pdf,
)
from services.tools.order import computeOrderAmount
from services.tools.order import getOrderContext
from services.tools.order_history import order_history
from services.tools.order_position import order_update_position
from services.tools.trailer_identification_to_pdf import trailer_identification_to_pdf
from services.views.invoice import get_invoice_context
from services.views.invoice import sendMail


@login_required
def update_order(request, id):
    # fetch the object related to passed id
    order = get_object_or_404(Order, id=id)

    form = OrderCreateForm(instance=order, get_plate=order.external)

    if request.method == "POST":
        # pass the object as instance in form
        form = OrderCreateForm(
            request.POST, instance=order, get_plate=order.external)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            return redirect("detail-service-order", id)

    # add form dictionary to context
    context = {"form": form, "order": order,
               "title": _("Update service order")}

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
def order_change_position(request, id):
    return order_update_position(
        request=request,
        id=id,
        next="detail-service-order",
        args=[id],
    )


@login_required
def order_change_position_from_storage(request, id):
    return order_update_position(
        request=request,
        id=id,
        next="storage-view",
    )


@login_required
def order_end_update_position(request, id, status):
    return order_update_position(request=request, id=id, status=status)


STATUS_ORDER = ["pending", "processing", "approved", "complete", "decline"]


@login_required
def list_order(request):
    context = prepareListOrder(
        request,
        ("processing", "pending"),
        pos_null=False,
        pos_storate=False,
    )
    context.setdefault(
        "alternative_views",
        [
            {
                "view": "list-service-order-terminated",
                "text": "Terminated",
            },
            # {
            #     "view": "list-service-order-terminated-on-pos",
            #     "text": "Ready to release",
            # },
        ],
    )
    return render(request, "services/order_list.html", context)


@login_required
def list_order_on_pos(request):
    status = [s[0] for s in Order.STATUS_CHOICE]
    context = prepareListOrder(
        request,
        # ("complete", "decline", "payment_pending"),
        status,
        pos_null=False,
        pos_storate=False,
    )
    # context.setdefault(
    #     "alternative_views",
    #     [
    #         {
    #             "view": "list-service-order",
    #             "text": "Active",
    #         },
    #         {
    #             "view": "list-service-order-terminated",
    #             "text": "Terminated",
    #         },
    #     ],
    # )
    return render(request, "services/order_list.html", context)


@login_required
def list_terminated_order(request, year=None, month=None):
    (
        (previousMonth, previousYear),
        (currentMonth, currentYear),
        (nextMonth, nextYear),
    ) = getMonthYear(month, year)

    context = preparePaginatedListOrder(
        request, ("complete", "decline",
                  "payment_pending"), currentYear, currentMonth
    )
    context.setdefault(
        "alternative_views",
        [
            {
                "view": "list-service-order",
                "text": "Active",
            },
            # {
            #     "view": "list-service-order-terminated-on-pos",
            #     "text": "Ready to release",
            # },
        ],
    )

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


def prepareListOrder(
    request, status_list, pos_18=True, pos_storate=True, pos_null=True
):
    # positions = []
    # if pos_18:
    #     for i in range(1, 9):
    #         positions.append(i)
    # if pos_storate:
    #     positions.append(0)
    # if pos_null:
    #     positions.append(None)

    # List orders
    orders = Order.objects.filter(
        type="sell",
        status__in=status_list,
        # position__in=positions,
    ).order_by("-created_date")

    if not pos_18:
        positions = [i for i in range(1, 9)]
        orders = orders.exclude(position__in=positions)

    if not pos_storate:
        orders = orders.exclude(position=0)

    if not pos_null:
        orders = orders.exclude(
            # ~Q(concept=PARTS_SALE),
            # quotation=False,
            position=None,
        )

    # orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    orders = sorted(orders, key=lambda x: 0 if x.status ==
                    "payment_pending" else 1)

    statuses = set()
    for order in orders:
        statuses.add(order.status)
        # transactions = ProductTransaction.objects.filter(order=order)
        computeOrderAmount(order)
    return {"orders": orders, "statuses": statuses}


def preparePaginatedListOrder(request, status_list, currentYear, currentMonth):
    # List orders
    orders = Order.objects.filter(
        type="sell",
        status__in=status_list,
        created_date__year=currentYear,
        created_date__month=currentMonth,
    ).order_by("-created_date")

    orders = sorted(orders, key=lambda x: 0 if x.status ==
                    "payment_pending" else 1)

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
    order.decline_reazon = OrderDeclineReazon.objects.filter(
        order=order,
    ).last()

    client = order.associated
    if client is not None:
        orders = Order.objects.filter(
            ~Q(id=order.id),
            associated=client,
            created_date__lt=order.created_date,
        ).order_by("-created_date")
        for order in orders:
            computeOrderAmount(order)
        context.setdefault("history", orders)

    if context["terminated"]:
        # Payments
        context.setdefault(
            "payments", Payment.objects.filter(order=context["order"]))

    # partsFilter = request.GET['parts_filter'] if 'parts_filter' in request.GET else ''
    # servicesFilter = request.GET['services_filter'] if 'services_filter' in request.GET else ''
    # partsNumber = int(request.GET['parts_number']
    #                   if 'parts_number' in request.GET else 1)
    # servicesNumber = int(
    #     request.GET['services_number'] if 'services_number' in request.GET else 1)

    parts, pNum, pTotal, services, sNum, sTotal = order_history(
        order,
        # parts_filter=partsFilter,
        # services_filter=servicesFilter,
        # parts_number=partsNumber,
        # services_number=servicesNumber,
        get_all=True,
    )

    context["parts_history"] = parts
    context["parts_next"] = pNum + 5
    context["parts_number"] = pNum
    context["parts_total_count"] = pTotal
    context["services_history"] = services
    context["services_next"] = sNum + 5
    context["services_number"] = sNum
    context["services_total_count"] = sTotal

    context["psc_total"] = (
        context["parts_total"] + context["service_total"] +
        context["consumable_total"]
    )

    return render(request, "services/order_detail.html", context)


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
