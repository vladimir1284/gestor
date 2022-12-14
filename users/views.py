import os
from django.urls import reverse_lazy
from django.views.generic.edit import (
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import permission_required, login_required

from .forms import (
    ProviderCreateForm,
    UserProfileForm,
    UserCreateForm,
    AssociatedCreateForm,
    UserUpdateForm,
    CompanyCreateForm,
)

from .models import (
    User,
    UserProfile,
    Associated,
    Company,
)
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
        order_data = request.session.get('creating_order')
        if order_data is not None:
            form = AssociatedCreateForm(request.POST, request.FILES)
            if form.is_valid():
                client = form.save()
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
            associated = form.save()
            request.session['associated_id'] = associated.id
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


@login_required
def detail_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)
    return render(request, 'users/associated_detail.html', {'associated': associated,
                                                            'title': 'Associated detail'})


def list_associated(request, type):
    associateds = Associated.objects.filter(type=type, active=True)
    return render(request, 'users/associated_list.html', {'associateds': associateds,
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
    next = request.GET.get('next', 'list-company')
    if request.method == 'POST':
        form = CompanyCreateForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            order_data = request.session.get('creating_order')
            if order_data is not None:
                client_id = request.session.get('client_id')
                client = get_object_or_404(Associated, id=client_id)
                client.company = company
                request.session['company_id'] = company.id
                return redirect('select-equipment')
            else:
                order_id = request.session.get('order_detail')
                if order_id is not None:
                    order = get_object_or_404(Order, id=order_id)
                    order.company = company
                    order.save()
                    return redirect('detail-service-order', id=order_id)
            return redirect(next)
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
    if request.method == 'POST':
        company = get_object_or_404(Company, id=request.POST.get('id'))
        request.session['company_id'] = company.id
        order_data = request.session.get('creating_order')
        if order_data is not None:
            return redirect('select-equipment')
        else:
            order_id = request.session.get('order_detail')
            if order_id is not None:
                order = get_object_or_404(Order, id=order_id)
                order.company = company
                order.save()
                return redirect('detail-service-order', id=order_id)
        next = request.GET.get('next', 'list-company')
        return redirect(next)
    companies = Company.objects.filter(active=True).order_by("-created_date")
    return render(request, 'users/company_select.html', {'companies': companies})


@login_required
def list_company(request):
    companies = Company.objects.filter(active=True).order_by("-created_date")
    for company in companies:
        last_order = Order.objects.filter(
            company=company).order_by("-created_date").first()
        if last_order:
            company.last_order = last_order
    return render(request, 'users/company_list.html', {'companies': companies})


@ login_required
def delete_company(request, id):
    # fetch the object related to passed id
    company = get_object_or_404(Company, id=id)
    company.active = False
    company.save()
    return redirect('list-company')
