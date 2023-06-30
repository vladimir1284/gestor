from typing import List
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from users.views import processOrders
from users.models import Company
from rent.models.vehicle import (
    Trailer,
    Manufacturer,
    TrailerPicture,
)
from utils.models import (
    Order,
)
from rent.forms.vehicle import (
    TrailerCreateForm,
    ManufacturerForm,
    TrailerPictureForm,
)
from django.utils.translation import gettext_lazy as _

# -------------------- Equipment ----------------------------


@login_required
def list_equipment(request):
    trailers = Trailer.objects.all()
    for trailer in trailers:
        last_order = Order.objects.filter(
            trailer=trailer).order_by("-created_date").first()
        if last_order is not None:
            trailer.last_order = last_order
    context = {
        'trailers': trailers,
    }
    return render(request, 'rent/equipment_list.html', context)


def appendEquipment(request, id):
    order_id = request.session.get('order_detail')
    if order_id is not None:
        order = get_object_or_404(Order, id=order_id)
    trailer = Trailer.objects.get(id=id)
    order.trailer = trailer
    order.equipment_type = 'trailer'
    order.save()
    return redirect('detail-service-order', id=order_id)


@login_required
def select_towit(request):
    # Create the Towithouston company if it doesn't exists
    company, created = Company.objects.get_or_create(
        name='Towithouston',
        defaults={'name': 'Towithouston'}
    )
    request.session['company_id'] = company.id
    return redirect('select-company', request=request)


@login_required
def select_trailer(request):
    order_id = None
    if request.method == 'POST':
        order_data = request.session.get('creating_order')
        id = request.POST.get('id')
        if order_data is not None:
            trailer = Trailer.objects.get(id=id)
            request.session['trailer_id'] = trailer.id
            return redirect('create-service-order')
        return appendEquipment(request, id)

    if type == 'trailer':
        trailers = Trailer.objects.all().order_by('-year')
        context = {
            'trailers': trailers,
        }
    try:
        context.setdefault("type", type)
    except Exception as err:
        print(err)
        trailers = Trailer.objects.all()
        context = {
            'trailers': trailers,
        }
    if order_id is not None:
        context.setdefault('skip', False)
    else:
        context.setdefault('skip', True)

    return render(request, 'rent/equipment_select.html', context)


# -------------------- Trailer ----------------------------


@login_required
def create_trailer(request):
    form = TrailerCreateForm()
    if request.method == 'POST':
        form = TrailerCreateForm(request.POST, request.FILES)
        if form.is_valid():
            trailer = form.save()
            order_data = request.session.get('creating_order')
            request.session['trailer_id'] = trailer.id
            if order_data is not None:
                return redirect('create-service-order')
            return appendEquipment(request, trailer.id)

    context = {
        'form': form,
        'title': _("Create Trailer")
    }
    return render(request, 'rent/equipment_create.html', context)


@login_required
def update_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)

    # pass the object as instance in form
    form = TrailerCreateForm(request.POST or None,
                             request.FILES or None,
                             instance=trailer)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-trailer', id)

    # add form dictionary to context
    if not Order.objects.filter(trailer=trailer):
        trailer.can_delete = True

    context = {
        'form': form,
        'trailer': trailer,
        'title': _("Update Trailer")
    }

    return render(request, 'rent/equipment_create.html', context)


@login_required
def detail_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)
    orders = Order.objects.filter(trailer=trailer).order_by("-created_date")
    processOrders(orders)
    context = {
        'orders': orders,
        'equipment': trailer,
        'type': 'trailer',
        'title': _("Trailer details")
    }

    return render(request, 'rent/equipment_detail.html', context)


@login_required
def delete_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)
    trailer.delete()
    return redirect('list-equipment', id=trailer.order.id)


# -------------------- Manufacturer ----------------------------

def manufacturer_list(request):
    manufacturers = Manufacturer.objects.all()
    return render(request, 'manufacturer_list.html', {'manufacturers': manufacturers})


def manufacturer_create(request):
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manufacturer-list')
    else:
        form = ManufacturerForm()
    return render(request, 'manufacturer_create.html', {'form': form})


def manufacturer_update(request, pk):
    manufacturer = Manufacturer.objects.get(pk=pk)
    if request.method == 'POST':
        form = ManufacturerForm(
            request.POST, request.FILES, instance=manufacturer)
        if form.is_valid():
            form.save()
            return redirect('manufacturer-list')
    else:
        form = ManufacturerForm(instance=manufacturer)
    return render(request, 'manufacturer_create.html', {'form': form})


def manufacturer_delete(request, pk):
    manufacturer = Manufacturer.objects.get(pk=pk)
    manufacturer.delete()
    return redirect('manufacturer-list')


# -------------------- Picture ----------------------------

def trailer_picture_create(request, trailer_id):
    """
    Create a new TrailerPicture object for the specified Trailer.
    """
    trailer = get_object_or_404(Trailer, pk=trailer_id)

    if request.method == 'POST':
        form = TrailerPictureForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.save(commit=False)
            picture.trailer = trailer
            picture.save()
            return redirect('detail-trailer', trailer_id=trailer_id)
    else:
        form = TrailerPictureForm()

    context = {'form': form, 'trailer': trailer}
    return render(request, 'trailer_picture_create.html', context)


def trailer_picture_update(request, pk):
    """
    Update an existing TrailerPicture object.
    """
    trailer_picture = get_object_or_404(TrailerPicture, pk=pk)
    if request.method == 'POST':
        form = TrailerPictureForm(
            request.POST, request.FILES, instance=trailer_picture)
        if form.is_valid():
            form.save()
            return redirect('detail-trailer', trailer_id=trailer_picture.trailer.id)
    else:
        form = TrailerPictureForm(instance=trailer_picture)
    context = {'form': form}
    return render(request, 'trailer_picture_create.html', context)


def trailer_picture_delete(request, pk):
    """
    Delete an existing TrailerPicture object.
    """
    trailer_picture = get_object_or_404(TrailerPicture, pk=pk)
    if request.method == 'POST':
        trailer_picture.delete()
        return redirect('detail-trailer', trailer_id=trailer_picture.trailer.id)
