from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from services.models import ServiceTransaction

from inventory.models import (
    Product,
    Unit,
)
from inventory.forms import (
    UnitCreateForm,
)
from django.utils.translation import gettext_lazy as _

# -------------------- Unit ----------------------------


@login_required
def create_unit(request):
    form = UnitCreateForm()
    if request.method == 'POST':
        form = UnitCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-unit')
    context = {
        'form': form
    }
    return render(request, 'inventory/unit_create.html', context)


@login_required
def update_unit(request, id):
    # fetch the object related to passed id
    unit = get_object_or_404(Unit, id=id)
    if not Product.objects.filter(unit=unit):
        unit.can_delete = True

    # pass the object as instance in form
    form = UnitCreateForm(request.POST or None,
                          instance=unit)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('list-unit')

    # add form dictionary to context
    context = {
        'form': form,
    }

    return render(request, 'inventory/unit_update.html', context)


@login_required
def list_unit(request):
    units = Unit.objects.all()
    return render(request, 'inventory/unit_list.html', {'units': units})


@login_required
def delete_unit(request, id):
    # fetch the object related to passed id
    unit = get_object_or_404(Unit, id=id)
    unit.delete()
    return redirect('list-unit')
