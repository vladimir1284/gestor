from typing import List
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from .models import (
    Trailer,
    Vehicle,
)
from utils.models import (
    Order,
)
from .forms import (
    TrailerCreateForm,
    VehicleCreateForm,
    EquipmentTypeForm,
)
from django.utils.translation import gettext_lazy as _

# -------------------- Equipment ----------------------------


@login_required
def list_equipment(request):
    trailers = Trailer.objects.all()
    vehicles = Vehicle.objects.all()
    context = {
        'trailers': trailers,
        'vehicles': vehicles,
    }
    return render(request, 'equipment/list_equipment.html', context)


@login_required
def select_equipment(request):
    type = request.session.get("equipment_type")
    order_id = None
    if type is None:
        order_id = request.session.get('order_detail')
        order = get_object_or_404(Order, id=order_id)
        type = order.equipment_type
    if request.method == 'POST':
        if type is None:
            type = request.POST.get('type')
        order_data = request.session.get('creating_order')
        if order_data is not None:
            if type == 'trailer':
                trailer = Trailer.objects.get(
                    id=request.POST.get('id'))
                request.session['trailer_id'] = trailer.id
            elif type == 'vehicle':
                vehicle = Vehicle.objects.get(id=request.POST.get('id'))
                request.session['vehicle_id'] = vehicle.id
            return redirect('create-service-order')
        else:
            # order_id = request.session.get('order_detail')
            # if order_id is not None:
            #     order = get_object_or_404(Order, id=order_id)
            if type == 'trailer':
                trailer = Trailer.objects.get(
                    id=request.POST.get('id'))
                order.trailer = trailer
                order.equipment_type = 'trailer'
            elif type == 'vehicle':
                vehicle = Vehicle.objects.get(id=request.POST.get('id'))
                order.vehicle = vehicle
                order.equipment_type = 'vehicle'
            order.save()
            return redirect('detail-service-order', id=order_id)

    if type == 'trailer':
        trailers = Trailer.objects.all()
        context = {
            'trailers': trailers,
        }
    if type == 'vehicle':
        vehicles = Vehicle.objects.all()
        context = {
            'vehicles': vehicles,
        }
    try:
        context.setdefault("type", type)
    except Exception as err:
        print(err)
        trailers = Trailer.objects.all()
        vehicles = Vehicle.objects.all()
        context = {
            'trailers': trailers,
            'vehicles': vehicles,
        }
    if order_id is not None:
        context.setdefault('skip', False)
    else:
        context.setdefault('skip', True)

    return render(request, 'equipment/equipment_select.html', context)


@login_required
def select_equipment_type(request):
    form = EquipmentTypeForm()
    if request.method == 'POST':
        form = EquipmentTypeForm(request.POST)
        if form.is_valid():
            request.session["equipment_type"] = form.cleaned_data['type']
            return redirect('select-equipment')
    context = {
        'form': form
    }
    return render(request, 'equipment/equipment_type_select.html', context)


# -------------------- Trailer ----------------------------


@login_required
def create_trailer(request):
    form = TrailerCreateForm()
    if request.method == 'POST':
        form = TrailerCreateForm(request.POST, request.FILES)
        if form.is_valid():
            trailer = form.save()
            order_data = request.session.get('creating_order')
            if order_data is not None:
                request.session['trailer_id'] = trailer.id
            return redirect('create-service-order')
    context = {
        'form': form,
        'title': _("Create Trailer")
    }
    return render(request, 'equipment/equipment_create.html', context)


@login_required
def update_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)

    # pass the object as instance in form
    form = TrailerCreateForm(request.POST or None,
                             instance=trailer)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # add form dictionary to context
    if not Order.objects.filter(trailer=trailer):
        trailer.can_delete = True

    context = {
        'form': form,
        'trailer': trailer,
        'title': _("Update Trailer")
    }

    return render(request, 'equipment/equipment_create.html', context)


@login_required
def delete_trailer(request, id):
    # fetch the object related to passed id
    trailer = get_object_or_404(Trailer, id=id)
    trailer.delete()
    return redirect('list-equipment', id=trailer.order.id)


# -------------------- Vehicle ----------------------------


@login_required
def create_vehicle(request):
    form = VehicleCreateForm()
    if request.method == 'POST':
        form = VehicleCreateForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save()
            order_data = request.session.get('creating_order')
            if order_data is not None:
                request.session['vehicle_id'] = vehicle.id
            return redirect('create-service-order')
    context = {
        'form': form,
        'title': _("Create Car")
    }
    return render(request, 'equipment/equipment_create.html', context)


@login_required
def update_vehicle(request, id):
    # fetch the object related to passed id
    vehicle = get_object_or_404(Vehicle, id=id)

    # pass the object as instance in form
    form = VehicleCreateForm(request.POST or None,
                             instance=vehicle)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # add form dictionary to context
    if not Order.objects.filter(vehicle=vehicle):
        vehicle.can_delete = True

    context = {
        'form': form,
        'vehicle': vehicle,
        'title': _("Update Car")
    }

    return render(request, 'equipment/equipment_create.html', context)


@login_required
def delete_vehicle(request, id):
    # fetch the object related to passed id
    vehicle = get_object_or_404(Vehicle, id=id)
    vehicle.delete()
    return redirect('list-equipment', id=vehicle.order.id)
