from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from .tracker import Tracker
from rent.forms.vehicle import ManufacturerForm
from rent.forms.vehicle import TrailerCreateForm
from rent.forms.vehicle import TrailerDocumentForm
from rent.forms.vehicle import TrailerDocumentUpdateForm
from rent.forms.vehicle import TrailerPictureForm
from rent.models.lease import Contract
from rent.models.trailer_deposit import get_current_trailer_deposit
from rent.models.vehicle import Manufacturer
from rent.models.vehicle import Trailer
from rent.models.vehicle import TrailerDocument
from rent.models.vehicle import TrailerPicture
from rent.models.vehicle import TrailerPlates
from rent.permissions import staff_required
from users.models import Company
from users.views import processOrders
from utils.models import (
    Order,
)

# -------------------- Equipment ----------------------------


@login_required
def list_equipment(request):
    active_filters = {
        "Available": 0,
        "Reserved": 0,
        "Rented": 0,
        "LTO": 0,
    }
    trailers = Trailer.objects.filter(active=True)
    for trailer in trailers:
        # Contracts
        contracts = Contract.objects.filter(trailer=trailer).exclude(stage="ended")
        if contracts:
            trailer.current_contract = contracts.last()
            _, trailer.paid = trailer.current_contract.paid()
            if trailer.current_contract.contract_type == "lto":
                trailer.filter = "LTO"
            else:
                trailer.filter = "Rented"

        trailer_deposits = get_current_trailer_deposit(trailer)
        if trailer_deposits:
            trailer.reservation = trailer_deposits
            if not hasattr(trailer, "filter"):
                trailer.filter = "Reserved"

        if not hasattr(trailer, "filter"):
            trailer.filter = "Available"

        active_filters[trailer.filter] += 1

        # Images
        images, pinned_image = getImages(trailer)
        trailer.images = images
        trailer.pinned_image = pinned_image
        # Documents
        doc_color = None
        docs = TrailerDocument.objects.filter(trailer=trailer, is_active=True)
        if docs:
            doc_color = "green"
        for doc in docs:
            if doc.remainder():
                doc_color = "orange"
            if doc.is_expired():
                doc_color = "red"
                break
        if doc_color is not None:
            trailer.doc_color = f"assets/img/icons/doc_{doc_color}.png"
        # Orders
        last_order = (
            Order.objects.filter(trailer=trailer).order_by("-created_date").first()
        )
        if last_order is not None:
            trailer.last_order = last_order

    inactive_filters = {
        "Available": 0,
        "Rented": 0,
        "LTO": 0,
    }
    inactive_trailers = Trailer.objects.filter(active=False)
    for trailer in inactive_trailers:
        # Contracts
        contracts = Contract.objects.filter(trailer=trailer).exclude(stage="ended")
        if contracts:
            trailer.current_contract = contracts.last()
            trailer.paid = trailer.current_contract.paid()
            if trailer.current_contract.contract_type == "lto":
                trailer.filter = "LTO"
            else:
                trailer.filter = "Rented"

        if not hasattr(trailer, "filter"):
            trailer.filter = "Available"

        inactive_filters[trailer.filter] += 1

        # Images
        images, pinned_image = getImages(trailer)
        trailer.images = images
        trailer.pinned_image = pinned_image
        # Documents
        doc_color = None
        docs = TrailerDocument.objects.filter(trailer=trailer, is_active=True)
        if docs:
            doc_color = "green"
        for doc in docs:
            if doc.remainder():
                doc_color = "orange"
            if doc.is_expired():
                doc_color = "red"
                break
        if doc_color is not None:
            trailer.doc_color = f"assets/img/icons/doc_{doc_color}.png"
        # Orders
        last_order = (
            Order.objects.filter(trailer=trailer).order_by("-created_date").first()
        )
        if last_order is not None:
            trailer.last_order = last_order

    context = {
        "trailers": trailers,
        "inactive_trailers": inactive_trailers,
        "active_filters": active_filters,
        "inactive_filters": inactive_filters,
    }
    return render(request, "rent/equipment_list.html", context)


def appendEquipment(request, id):
    order_id = request.session.get("order_detail")
    if order_id is not None:
        order = get_object_or_404(Order, id=order_id)
    trailer = Trailer.objects.get(id=id)
    order.trailer = trailer
    order.equipment_type = "trailer"
    order.save()
    return redirect("detail-service-order", id=order_id)


@login_required
def select_towit(request):
    # Create the Towithouston company if it doesn't exists
    company, created = Company.objects.get_or_create(
        name="Towithouston", defaults={"name": "Towithouston"}
    )
    request.session["company_id"] = company.id
    return redirect("select-company", request=request)


@login_required
def select_trailer(request):
    order_id = None
    if request.method == "POST":
        order_data = request.session.get("creating_order")
        id = request.POST.get("id")
        if order_data is not None:
            trailer = Trailer.objects.get(id=id)
            request.session["trailer_id"] = trailer.id
            return redirect("create-service-order")
        return appendEquipment(request, id)

    trailers = Trailer.objects.all().order_by("-year")
    for trailer in trailers:
        images, pinned_image = getImages(trailer)
        trailer.images = images
        trailer.pinned_image = pinned_image
    context = {
        "trailers": trailers,
    }
    if order_id is not None:
        context.setdefault("skip", False)
    else:
        context.setdefault("skip", True)

    return render(request, "rent/equipment_select.html", context)


# -------------------- Trailer ----------------------------


@login_required
@staff_required
def create_trailer(request):
    form = TrailerCreateForm()
    if request.method == "POST":
        form = TrailerCreateForm(request.POST, request.FILES)
        if form.is_valid():
            trailer = form.save()
            TrailerPlates.objects.create(
                plate=trailer.plate, trailer=trailer, active_plate=True
            )
            # order_data = request.session.get('creating_order')
            return redirect("detail-trailer", trailer.id)
            # request.session['trailer_id'] = trailer.id
            # if order_data is not None:
            #     return redirect('create-service-order')
            # return appendEquipment(request, trailer.id)

    context = {"form": form, "title": _("Create Trailer")}
    return render(request, "rent/equipment_create.html", context)


@login_required
@staff_required
def update_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)

    # pass the object as instance in form
    form = TrailerCreateForm(
        request.POST or None, request.FILES or None, instance=trailer
    )

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        active_plate = TrailerPlates.objects.all().filter(
            trailer=trailer, active_plate=True
        )[0]
        updated_trailer = form.save()
        if not updated_trailer.plate == active_plate.plate:
            active_plate.active_plate = False
            active_plate.save()
            TrailerPlates.objects.create(
                plate=updated_trailer.plate, trailer=updated_trailer, active_plate=True
            )

        return redirect("detail-trailer", id)

    # add form dictionary to context
    if not Order.objects.filter(trailer=trailer):
        trailer.can_delete = True

    context = {"form": form, "trailer": trailer, "title": _("Update Trailer")}

    return render(request, "rent/equipment_create.html", context)


def getImages(trailer: Trailer):
    images = TrailerPicture.objects.filter(trailer=trailer)
    pinned_image = None
    for image in images:
        if image.pinned:
            pinned_image = image
            break
    return (images, pinned_image)


FILES_ICONS = {
    "PDF": "icn_pdf.svg",
    "DOC": "icn_doc.svg",
    "XLS": "icn_xlm.svg",
    "IMG": "icn_png.svg",
    "ZIP": "icn_zip.svg",
    "BIN": "icn_bin.png",
}


@login_required
def detail_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)
    orders = Order.objects.filter(trailer=trailer).order_by("-created_date")
    images, pinned_image = getImages(trailer)

    # Contracts
    contracts = Contract.objects.filter(trailer=trailer).exclude(stage="ended")
    if contracts:
        trailer.current_contract = contracts.last()

    trailer_deposits = get_current_trailer_deposit(trailer)
    if trailer_deposits:
        trailer.reservation = trailer_deposits

    documents = TrailerDocument.objects.filter(trailer=trailer, is_active=True)
    # Check for document expiration
    for document in documents:
        document.is_expired = document.is_expired()
        document.alarm = document.remainder()
        document.icon = "assets/img/icons/" + FILES_ICONS[document.document_type]
    # Get tracker
    trailer.tracker = Tracker.objects.filter(trailer=trailer).first()

    processOrders(orders)

    # Separate the towit orders
    towit_total = 0
    client_total = 0
    for order in orders:
        if order.status == "complete":
            if order.associated is None:
                towit_total += order.amount
            else:
                client_total += order.amount

    context = {
        "orders": orders,
        "towit_total": towit_total,
        "client_total": client_total,
        "documents": documents,
        "equipment": trailer,
        "pinned_image": pinned_image,
        "images": images,
        "type": "trailer",
        "title": _("Trailer details"),
    }

    return render(request, "rent/equipment_detail.html", context)


@login_required
@staff_required
def delete_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)
    trailer.delete()
    return redirect("list-equipment", id=trailer.order.id)


# -------------------- Manufacturer ----------------------------


@login_required
def manufacturer_list(request):
    manufacturers = Manufacturer.objects.all()
    return render(
        request, "rent/manufacturer_list.html", {"manufacturers": manufacturers}
    )


@login_required
@staff_required
def manufacturer_create(request):
    if request.method == "POST":
        form = ManufacturerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("manufacturer-list")
    else:
        form = ManufacturerForm()
    context = {"form": form, "title": _("Create manufacturer")}
    return render(request, "rent/manufacturer_create.html", context)


@login_required
@staff_required
def manufacturer_update(request, pk):
    manufacturer = Manufacturer.objects.get(pk=pk)
    if request.method == "POST":
        form = ManufacturerForm(request.POST, request.FILES, instance=manufacturer)
        if form.is_valid():
            form.save()
            return redirect("manufacturer-list")
    else:
        form = ManufacturerForm(instance=manufacturer)
    context = {"form": form, "title": _("Update manufacturer")}
    return render(request, "rent/manufacturer_create.html", context)


@login_required
@staff_required
def manufacturer_delete(request, pk):
    manufacturer = Manufacturer.objects.get(pk=pk)
    manufacturer.delete()
    return redirect("manufacturer-list")


# -------------------- Picture ----------------------------


@login_required
def trailer_picture_create(request, trailer_id):
    """
    Create a new TrailerPicture object for the specified Trailer.
    """
    trailer = get_object_or_404(Trailer, pk=trailer_id)

    if request.method == "POST":
        form = TrailerPictureForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.save(commit=False)
            picture.trailer = trailer
            picture.save()
            return redirect("detail-trailer", id=trailer_id)
    else:
        form = TrailerPictureForm()

    context = {"form": form, "trailer": trailer}
    return render(request, "rent/trailer_picture_create.html", context)


def share_pictures(request, ids):
    pks = list(map(int, ids.split(",")[:-1]))
    pictures = TrailerPicture.objects.filter(pk__in=pks)
    return render(
        request,
        "rent/trailer_pictures.html",
        {"images": pictures, "trailer": pictures[0].trailer},
    )


@login_required
@staff_required
def delete_trailer_pictures(request, ids):
    """
    Delete an existing TrailerPicture object.
    """
    pks = list(map(int, ids.split(",")[:-1]))
    pictures = TrailerPicture.objects.filter(pk__in=pks)
    trailer_id = pictures[0].trailer.id
    for img in pictures:
        img.delete()
    return redirect("detail-trailer", id=trailer_id)


@login_required
def update_pinned_picture(request, pk):
    # Get the TrailerPicture instance to update
    picture = get_object_or_404(TrailerPicture, pk=pk)

    # Set the pinned attribute of the selected picture to True
    picture.pinned = True
    picture.save()

    # Set the pinned attribute of all other pictures related to the same trailer to False
    trailer_pictures = TrailerPicture.objects.filter(trailer=picture.trailer).exclude(
        pk=pk
    )
    trailer_pictures.update(pinned=False)

    return redirect("detail-trailer", id=picture.trailer.id)


# -------------------- Document ----------------------------


@login_required
def create_document(request, trailer_id):
    trailer = get_object_or_404(Trailer, id=trailer_id)
    if request.method == "POST":
        form = TrailerDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.trailer = trailer
            document.save()
            messages.success(request, "Document created successfully.")
            return redirect("detail-trailer", id=trailer_id)
    else:
        form = TrailerDocumentForm()

    context = {"form": form, "title": _("Add document")}
    return render(request, "rent/trailer_document_create.html", context)


@login_required
@staff_required
def update_document(request, id):
    document = get_object_or_404(TrailerDocument, id=id)
    form = TrailerDocumentUpdateForm(
        request.POST or None, request.FILES or None, instance=document
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Document updated successfully.")
            return redirect("detail-trailer", id=document.trailer.id)

    context = {"form": form, "title": _("Update document")}
    return render(request, "rent/trailer_document_create.html", context)


@login_required
@staff_required
def delete_document(request, id):
    document = get_object_or_404(TrailerDocument, id=id)
    document.delete()
    messages.success(request, "Document deleted successfully.")
    return redirect("detail-trailer", id=document.trailer.id)


# @login_required
# def document_detail(request, trailer_id, id):
#     trailer = get_object_or_404(Trailer, id=trailer_id)
#     document = get_object_or_404(
#         TrailerDocument, id=id, trailer=trailer)
#     return render(request, 'document_detail.html', {'document': document})

# @login_required
# def trailer_json(request, id):
#     trailer = Trailer.objects.get(id=id)
#     return JsonResponse({'type': trailer.type.name,
#                          'size': trailer.size,
#                          'id': trailer.id,
#                          'current_tires_condition': trailer.get_current_tires_condition_display(),
#                          'number_of_axles': trailer.get_number_of_axles_display(),
#                          'bed_type': trailer.get_bed_type_display(),
#                          'bed_comments': trailer.bed_comments,
#                          'has_spare_tire': trailer.get_has_spare_tire_display(),
#                          'number_of_ramps': trailer.number_of_ramps,
#                          'ramps_material': trailer.get_ramps_material_display(),
#                          'ramps_length': trailer.get_ramps_length_display(),
#                          'electrical_instalation': trailer.electrical_instalation})
