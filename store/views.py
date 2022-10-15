from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required

from users.models import User
from .models import (
    Associated,
    Product,
    Unit,
    Order,
    Transaction,
    StoreLocations,
    ProductCategory,
)
from .forms import (
    UnitCreateForm,
    ProductCreateForm,
    CategoryCreateForm,
    AssociatedCreateForm
)


class DifferentMagnitudeUnitsError(BaseException):
    """
    Raised when the input and output units
    doesn't measure the same magnitude
    """
    pass


def convertUnit(input_unit, output_unit, value):
    iu = Unit.objects.get(name=input_unit)
    ou = Unit.objects.get(name=output_unit)
    if (iu.magnitude != ou.magnitude):
        raise DifferentMagnitudeUnitsError
    return value*iu.factor/ou.factor


@login_required
def create_category(request):
    form = CategoryCreateForm()
    if request.method == 'POST':
        form = CategoryCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            ProductCategory.objects.create(name=name)
            return redirect('/store/list-category')
    context = {
        'form': form
    }
    return render(request, 'store/addCategory.html', context)


@login_required
def create_unit(request):
    form = UnitCreateForm()
    if request.method == 'POST':
        form = UnitCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            factor = form.cleaned_data['factor']
            magnitude = form.cleaned_data['magnitude']
            Unit.objects.create(name=name,
                                factor=factor,
                                magnitude=magnitude)
            return redirect('/store/list-unit')
    context = {
        'form': form
    }
    return render(request, 'store/addUnit.html', context)


@login_required
def create_product(request):
    form = ProductCreateForm()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            unit = form.cleaned_data['unit']
            category = form.cleaned_data['category']
            type = form.cleaned_data['type']
            sell_price = form.cleaned_data['sell_price']
            sell_tax = form.cleaned_data['sell_tax']
            sell_price_min = form.cleaned_data['sell_price_min']
            sell_price_max = form.cleaned_data['sell_price_max']
            quantity_min = form.cleaned_data['quantity_min']
            image = form.cleaned_data['image']
            Product.objects.create(name=name,
                                   description=description,
                                   unit=unit,
                                   category=category,
                                   type=type,
                                   sell_price=sell_price,
                                   sell_tax=sell_tax,
                                   sell_price_min=sell_price_min,
                                   sell_price_max=sell_price_max,
                                   quantity_min=quantity_min,
                                   image=image
                                   )
            return redirect('/store/list-product')
    context = {
        'form': form
    }
    return render(request, 'store/addProduct.html', context)


@login_required
def create_associated(request):
    form = AssociatedCreateForm()
    if request.method == 'POST':
        form = AssociatedCreateForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            company = form.cleaned_data['company']
            address = form.cleaned_data['address']
            note = form.cleaned_data['note']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            type = form.cleaned_data['type']
            avatar = form.cleaned_data['avatar']
            Associated.objects.create(name=name,
                                   company=company,
                                   address=address,
                                   note=note,
                                   email=email,
                                   phone_number=phone_number,
                                   type=type,
                                   avatar=avatar
                                   )
            return redirect('/store/list-associated')
    context = {
        'form': form
    }
    return render(request, 'store/addAssociated.html', context)