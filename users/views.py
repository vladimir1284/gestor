import os
from typing import List
from services.views.order import computeOrderAmount
from datetime import datetime, timedelta
import pytz
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import permission_required, login_required

from .forms import (
    ProviderCreateForm,
    UserProfileForm,
    UserCreateForm,
    AssociatedCreateForm,
    UserUpdateForm,
    CompanyCreateForm,
)

from services.models import Payment

from .models import (
    User,
    UserProfile,
    Associated,
    Company,
)
from services.models import DebtStatus, PendingPayment
from utils.models import Order
from django.utils.translation import gettext_lazy as _


@permission_required('auth.user.can_add_user')
def create_user(request):
    form = UserProfileForm()
    userCform = UserCreateForm()
    if request.method == 'POST':
        userCform = UserCreateForm(request.POST)
        if userCform.is_valid():
            form = UserProfileForm(request.POST, request.FILES)
            if form.is_valid():
                user = userCform.save()
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                return redirect('list-user')
    context = {
        'form': form,
        'user_form': userCform
    }
    return render(request, 'users/user_create.html', context)


@login_required
def update_user(request, id):
    # fetch the object related to passed id
    profile = get_object_or_404(UserProfile, id=id)

    if profile.avatar:
        path = profile.avatar.path

    form = UserProfileForm(instance=profile)
    userCform = UserUpdateForm(instance=profile.user)

    if request.method == 'POST':
        userCform = UserUpdateForm(request.POST, instance=profile.user)
        if userCform.is_valid():
            form = UserProfileForm(
                request.POST, request.FILES, instance=profile)
            # save the data from the form and
            # redirect to detail_view
            if form.is_valid():
                profile.user.save()
                profile.save()
                if request.user.has_perm('auth.user.can_add_user'):
                    return redirect('list-user')
                return redirect('/')

    # add form dictionary to context
    context = {
        'form': form,
        'user_form': userCform
    }

    return render(request, 'users/user_update.html', context)


@permission_required('auth.user.can_add_user')
def list_user(request):
    profiles = UserProfile.objects.exclude(id=request.user.profile_user.id)
    print(profiles)
    return render(request, 'users/user_list.html', {'profiles': profiles})


@permission_required('auth.user.can_add_user')
def delete_user(request, id):
    # fetch the object related to passed id
    profile = get_object_or_404(UserProfile, id=id)
    profile.user.delete()  # Profile is deleted by cascade behavior
    return redirect('list-user')


# -------------------- Associated ----------------------------

FORMS = {'client': AssociatedCreateForm,
         'provider': ProviderCreateForm}


@login_required
def create_provider(request):
    return create_associated(request, 'provider')


@login_required
def create_client(request):
    if request.method == 'POST':
        form = AssociatedCreateForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save()

            order_data = request.session.get('creating_order')
            if order_data is not None:
                request.session['client_id'] = client.id
                return redirect('select-company')
            else:
                order_id = request.session.get('order_detail')
                if order_id is not None:
                    order = get_object_or_404(Order, id=order_id)
                    order.associated = client
                    order.save()
                    return redirect('detail-service-order', id=order_id)

    return create_associated(request, 'client')


def addStateCity(context):
    cities = {'texas': {'houston': 'Houston',
                        'dallas': 'Dallas',
                        'austin': 'Austin',
                        'san_antonio': 'San Antonio'
                        },
              'florida': {'miami': 'Miami',
                          'tampa': 'Tampa',
                          'orlando': 'Orlando',
                          'jacksonville': 'Jacksonville'
                          }
              }
    context.setdefault('cities', cities)


def create_associated(request, type):
    initial = {'type': type}
    form = FORMS[type](initial=initial)
    next = request.GET.get('next', 'list-{}'.format(type))
    if request.method == 'POST':
        form = FORMS[type](
            request.POST, request.FILES, initial=initial)
        if form.is_valid():
            associated: Associated = form.save()
            request.session['associated_id'] = associated.id
            if associated.outsource:
                order_id = request.session.get('order_detail')
                return redirect('create-expense', order_id)
            return redirect(next)
    title = {'client':  _('Create client'),
             'provider':  _('Create Provider')}[type]
    context = {
        'form': form,
        'title': title
    }
    addStateCity(context)
    return render(request, 'users/contact_create.html', context)


@login_required
def update_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)

    last_order = Order.objects.filter(
        associated=associated).order_by("-created_date").first()
    if not last_order:
        associated.delete_url = 'delete-associated'
    else:
        associated.last_order = last_order

    # pass the object as instance in form
    form = FORMS[associated.type](instance=associated)

    if request.method == 'POST':
        # pass the object as instance in form
        form = FORMS[associated.type](
            request.POST, request.FILES, instance=associated)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            if associated.type == 'client':
                return redirect('list-client')
            if associated.type == 'provider':
                return redirect('list-provider')

    # add form dictionary to context
    title = {'client':  _('Update client'),
             'provider':  _('Update Provider')}[associated.type]
    context = {
        'form': form,
        'title': title,
    }
    addStateCity(context)
    return render(request, 'users/contact_create.html', context)


@login_required
def list_provider(request):
    return list_associated(request, 'provider')


@login_required
def list_client(request):
    return list_associated(request, 'client')


def getDebtOrders(debtor):
    orders = Order.objects.filter(associated=debtor, type="sell",
                                  status="complete").order_by("-terminated_date")
    pending_orders = []
    debt = debtor.debt
    for order in orders:
        debt_payment = Payment.objects.filter(order=order,
                                              category__name="debt").first()
        if debt_payment is not None:
            # Order with pending payment
            if debt > 0:
                order.debt = debt_payment.amount
                pending_orders.append(order)
                debt -= debt_payment.amount
            else:
                break
    return pending_orders


@login_required
def list_debtor(request):
    context = get_debtor(request)
    return render(request, 'users/debtor_list.html', context)


def get_debtor(request):
    debtors: List[Associated] = Associated.objects.filter(
        debt__gt=0, active=True).order_by("name", "alias")
    total = 0
    debtors_list = []
    for client in debtors:
        debt_status = DebtStatus.objects.filter(client=client)[0]
        if debt_status.status == 'pending':
            try:
                client.oldest_debt = getDebtOrders(client)[0]
                total += client.debt
                debtors_list.append(client)
                client.overdue = client.oldest_debt.terminated_date < (
                    datetime.now(pytz.timezone('UTC')) - timedelta(days=14))
                client.last_order = Order.objects.filter(
                    associated=client).order_by("-created_date").first()
                if debt_status.weeks > 0:
                    client.weekly_payment = debt_status.amount_due_per_week
                    client.overdue = debt_status.last_modified_date < (
                        datetime.now(pytz.timezone('UTC')).date() - timedelta(days=7))
            except Exception as err:
                print(err)

    # Sort by last debt date
    debtors_list.sort(
        key=lambda x: x.oldest_debt.terminated_date, reverse=True)

    return {'associates': debtors_list,
            'total': total}


def processOrders(orders):
    orders.total = 0
    for order in orders:
        computeOrderAmount(order)
        order.amount += order.tax
        orders.total += order.amount


@login_required
def detail_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)
    pending_payments = PendingPayment.objects.filter(
        client=associated).order_by("-created_date")
    orders = Order.objects.filter(
        associated=associated).order_by("-created_date", "-id")
    processOrders(orders)
    if associated.debt > 0:
        pending_orders = getDebtOrders(associated)
        for order in orders:
            try:
                index = pending_orders.index(order)
                order.debt = pending_orders[index].debt
            except ValueError:
                pass  # Order without debt

    context = {'contact': associated,
               'orders': orders,
               'type': 'associated',
               'title': 'Associated detail',
               'pending_payments': pending_payments}

    return render(request, 'users/contact_detail.html', context)


def list_associated(request, type):
    associates = Associated.objects.filter(
        type=type, active=True).order_by("name", "alias")
    for associated in associates:
        associated.last_order = Order.objects.filter(
            associated=associated).order_by("-created_date").first()
    return render(request, 'users/associated_list.html', {'associates': associates,
                                                          'type': type})


@login_required
def delete_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)
    associated.active = False
    associated.save()
    return redirect('list-{}'.format(associated.type))


# -------------------- Company ----------------------------

@login_required
def create_company(request):
    form = CompanyCreateForm()
    if request.method == 'POST':
        form = CompanyCreateForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            order_data = request.session.get('creating_order')
            if order_data is not None:
                client_id = request.session.get('client_id')
                if client_id is not None:
                    client = get_object_or_404(Associated, id=client_id)
                    client.company = company
                request.session['company_id'] = company.id
                return redirect('select-equipment-type')
            else:
                order_id = request.session.get('order_detail')
                if order_id is not None:
                    order = get_object_or_404(Order, id=order_id)
                    order.company = company
                    order.save()
                    return redirect('detail-service-order', id=order_id)
            return redirect('list-company')
    context = {
        'form': form,
        'title': _('Create company')
    }
    addStateCity(context)
    return render(request, 'users/contact_create.html', context)


@login_required
def update_company(request, id):
    # fetch the object related to passed id
    company = get_object_or_404(Company, id=id)

    if not Order.objects.filter(company=company):
        company.delete_url = 'delete-company'

    # pass the object as instance in form
    form = CompanyCreateForm(request.POST or None,
                             request.FILES or None,
                             instance=company)

    # save the data from the form and
    # redirect to list_view
    if form.is_valid():
        form.save()
        return redirect('list-company')

    # add form dictionary to context
    context = {
        'form': form,
        'title': _('Update company')
    }
    addStateCity(context)
    return render(request, 'users/contact_create.html', context)


@login_required
def select_company(request):
    towit, created = Company.objects.get_or_create(
        name='Towithouston',
        defaults={'name': 'Towithouston'}
    )
    if request.method == 'POST':
        company = get_object_or_404(Company, id=request.POST.get('id'))
        request.session['company_id'] = company.id
        order_data = request.session.get('creating_order')
        if order_data is not None:
            if company.id == towit.id:
                return redirect('select-trailer')
            else:
                return redirect('create-service-order')
        else:
            order_id = request.session.get('order_detail')
            if order_id is not None:
                order = get_object_or_404(Order, id=order_id)
                order.company = company
                order.save()
                return redirect('detail-service-order', id=order_id)
        next = request.GET.get('next', 'list-company')
        return redirect(next)
    companies = Company.objects.filter(active=True).order_by("name", "alias")
    context = {'companies': companies,
               'towit': towit,
               'skip': True}
    order_id = request.session.get('order_detail')
    if order_id is not None:
        context['skip'] = False
    return render(request, 'users/company_select.html', context)


@login_required
def list_company(request):
    request.session['creating_order'] = None
    companies = Company.objects.filter(active=True).order_by("name", "alias")
    for company in companies:
        last_order = Order.objects.filter(
            company=company).order_by("-created_date").first()
        if last_order:
            company.last_order = last_order
    return render(request, 'users/company_list.html', {'companies': companies})


@login_required
def detail_company(request, id):
    # fetch the object related to passed id
    company = get_object_or_404(Company, id=id)
    orders = Order.objects.filter(
        company=company).order_by("-created_date", "-id")
    processOrders(orders)
    context = {'contact': company,
               'orders': orders,
               'type': 'company',
               'title': 'Company detail'}
    return render(request, 'users/contact_detail.html', context)


@ login_required
def delete_company(request, id):
    # fetch the object related to passed id
    company = get_object_or_404(Company, id=id)
    company.active = False
    company.save()
    return redirect('list-company')
