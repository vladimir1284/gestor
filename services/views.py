import os
from django.urls import reverse_lazy
from django.views.generic.edit import (
    UpdateView,
    CreateView,
    DeleteView,
)
from typing import List
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    HttpResponseRedirect)
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm

from users.models import (
    Associated,
)

from inventory.views import (
    getTransactionAmount,
    DifferentMagnitudeUnitsError,
    NotEnoughStockError,
)

from services.models import (
    Order,
)

from .models import (
    Service,
    Transaction,
    Profit,
    ServiceCategory,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    ServiceCreateForm,
    CategoryCreateForm,
    TransactionCreateForm,
)
from django.utils.translation import gettext_lazy as _

# -------------------- Category ----------------------------


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = ServiceCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-service-category')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-service-category')


class CategoryListView(LoginRequiredMixin, ListView):
    model = ServiceCategory
    template_name = 'services/category_list.html'


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(ServiceCategory, id=id)
    category.delete()
    return redirect('list-service-category')


# -------------------- Transaction ----------------------------


def renderCreateTransaction(request, form, service, order_id):
    context = {
        'form': form,
        'service': service,
        'order_id': order_id,
        'title': _("Create Transaction")
    }
    return render(request, 'services/transaction_create.html', context)


@login_required
def create_transaction(request, order_id, service_id):
    order = Order.objects.get(id=order_id)
    service = Service.objects.get(id=service_id)
    form = TransactionCreateForm(initial={'unit': service.unit})
    if request.method == 'POST':
        form = TransactionCreateForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.order = order
            trans.service = service
            trans.save()
            return redirect('detail-order', id=order_id)
    return renderCreateTransaction(request, form, service, order_id)


@login_required
def update_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)

    # pass the object as instance in form
    form = TransactionCreateForm(request.POST or None,
                                 instance=transaction)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-order', id=transaction.order.id)

    # add form dictionary to context
    context = {
        'form': form,
        'service': transaction.service,
        'order_id': transaction.order.id,
        'title': _("Update Transaction")
    }

    return render(request, 'services/transaction_create.html', context)


@login_required
def detail_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)
    return render(request, 'services/transaction_detail.html', {'transaction': transaction,
                                                                'amount': getTransactionAmount(transaction)})


def handle_transaction(transaction: Transaction, order: Order):
    pass


@login_required
def delete_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)
    transaction.delete()
    return redirect('detail-order', id=transaction.order.id)


# -------------------- Service ----------------------------

@login_required
def create_service(request):
    form = ServiceCreateForm()
    if request.method == 'POST':
        form = ServiceCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-service')
    context = {
        'form': form
    }
    return render(request, 'services/service_create.html', context)


@login_required
def update_service(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Service, id=id)

    # pass the object as instance in form
    form = ServiceCreateForm(request.POST or None,
                             instance=obj, title=_("Update Service"))

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('list-service')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'services/service_create.html', context)


def service_list_metadata(services: List[Service]):
    category_names = []
    categories = []
    for service in services:
        # Categories
        if service.category.name not in category_names:
            category_names.append(service.category.name)
            categories.append(service.category)
    return categories


def prepare_service_list():
    services = Service.objects.all()

    return {'services': services,
            'categories': service_list_metadata(services)}


@login_required
def list_service(request):
    response = prepare_service_list()
    return render(request, 'services/service_list.html', response)


@login_required
def select_service(request, next, order_id):
    response = prepare_service_list()
    response.setdefault("next", next)
    response.setdefault("order_id", order_id)
    return render(request, 'services/service_select.html', response)


@login_required
def select_new_service(request, next, order_id):
    form = ServiceCreateForm()
    if request.method == 'POST':
        form = ServiceCreateForm(request.POST)
        if form.is_valid():
            service = form.save()
            return redirect(next, order_id=order_id, service_id=service.id)
    context = {
        'form': form,
        'next': next,
        'order_id': order_id,
    }
    return render(request, 'services/service_create.html', context)


@login_required
def detail_service(request, id):
    # fetch the object related to passed id
    service = get_object_or_404(Service, id=id)
    purchases = Transaction.objects.filter(
        service=service, order__type='purchase').order_by('-order__created_date')
    latest_purchase = purchases.first()
    latest_order = None
    if latest_purchase:
        latest_order = latest_purchase.order
    return render(request, 'services/service_detail.html', {'service': service,
                                                            'purchases': purchases,
                                                            'latest_order': latest_order})


@login_required
def delete_service(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Service, id=id)
    obj.delete()
    return redirect('list-service')
