from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from services.models import Service

from inventory.models import (
    Product,
    convertUnit,
    ProductKit,
    KitElement,
    KitService
)
from inventory.forms import (
    KitCreateForm,
    KitElementCreateForm,
)
from django.utils.translation import gettext_lazy as _

from .product import (
    prepare_product_list,
    service_list_metadata,
)

# --------------------------- Kits --------------------------------


@login_required
def create_kit(request):
    form = KitCreateForm()
    if request.method == 'POST':
        form = KitCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-kit')
    context = {
        'form': form,
        'title': _("Create Kit")
    }
    return render(request, 'inventory/kit_create.html', context)


@login_required
def update_kit(request, id):
    # fetch the object related to passed id
    kit = get_object_or_404(ProductKit, id=id)

    # pass the object as instance in form
    form = KitCreateForm(request.POST or None,
                         instance=kit)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-kit', id)
    context = {
        'form': form,
        'title': _("Update kit")
    }

    return render(request, 'inventory/kit_create.html', context)


def computeKitData(kit):
    elements = KitElement.objects.filter(kit=kit)
    total = 0
    min_price = 0
    for element in elements:
        # Add cost
        total += element.quantity*convertUnit(
            element.product.unit,
            element.unit,
            element.product.getSuggestedPrice())
        min_price += element.quantity*convertUnit(
            element.product.unit,
            element.unit,
            element.product.min_price)
        # Compute availability
        element.product.available = convertUnit(
            element.product.unit,
            element.unit,
            element.product.computeAvailable())

    services = KitService.objects.filter(kit=kit)
    for service in services:
        total += service.service.suggested_price

    return (elements, services, total, min_price)


@login_required
def list_kit(request):
    kits = ProductKit.objects.all()

    for kit in kits:
        (elements, services, total, min_price) = computeKitData(kit)
        kit.total = total

    context = {
        'kits': kits,
    }
    return render(request, 'inventory/kit_list.html', context)


@login_required
def detail_kit(request, id):
    # fetch the object related to passed id
    kit = get_object_or_404(ProductKit, id=id)

    (elements, services, total, min_price) = computeKitData(kit)

    context = {
        'kit': kit,
        'elements': elements,
        'services': services,
        'total': total,
    }
    return render(request, 'inventory/kit_detail.html', context)


@ login_required
def delete_kit(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ProductKit, id=id)
    obj.delete()
    return redirect('list-kit')


# --------------------------- Kit Elements --------------------------------

@login_required
def select_kit_product(request, kit_id):
    active_products = Product.objects.filter(active=True)
    context = prepare_product_list(active_products)

    # Adding services to kit
    services = Service.objects.all()
    context.setdefault('services', services)
    context.setdefault('categories', service_list_metadata(services))
    context.setdefault("kit_id", kit_id)
    context.setdefault("title", _("Services and Products"))
    return render(request, 'inventory/kit_product_select.html', context)


@login_required
def create_kit_element(request, kit_id, product_id):
    product = get_object_or_404(Product, id=product_id)
    kit = get_object_or_404(ProductKit, id=kit_id)

    form = KitElementCreateForm(initial={'unit': product.unit})
    if request.method == 'POST':
        form = KitElementCreateForm(request.POST)
        if form.is_valid():
            kitElement = form.save(commit=False)
            kitElement.kit = kit
            kitElement.product = product
            kitElement.save()
            return redirect('detail-kit', kit_id)
    context = {
        'form': form,
        'kit': kit,
        'product': product,
        'title': _("Add kit product")
    }
    return render(request, 'inventory/kit_element_create.html', context)


@login_required
def update_kit_element(request, id):
    # fetch the object related to passed id
    kitElement = get_object_or_404(KitElement, id=id)

    # pass the object as instance in form
    form = KitElementCreateForm(request.POST or None,
                                instance=kitElement)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-kit', kitElement.kit.id)
    context = {
        'form': form,
        'title': _("Update kit product")
    }

    return render(request, 'inventory/kit_element_create.html', context)


@ login_required
def delete_kit_element(request, id):
    # fetch the object related to passed id
    kitElement = get_object_or_404(KitElement, id=id)
    kitElement.delete()
    return redirect('detail-kit', kitElement.kit.id)


# --------------------------- Kit Services --------------------------------


@login_required
def create_kit_service(request, kit_id, service_id):
    service = get_object_or_404(Service, id=service_id)
    kit = get_object_or_404(ProductKit, id=kit_id)

    KitService.objects.create(kit=kit, service=service)
    return redirect('detail-kit', kit_id)


@ login_required
def delete_kit_service(request, id):
    # fetch the object related to passed id
    kitService = get_object_or_404(KitService, id=id)
    kitService.delete()
    return redirect('detail-kit', kitService.kit.id)
