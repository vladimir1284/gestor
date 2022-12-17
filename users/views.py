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


@permission_required('auth.user.can_add_user')
def create_user(request):
    form = UserProfileForm()
    userCform = UserCreateForm()
    if request.method == 'POST':
        userCform = UserCreateForm(request.POST)
        if userCform.is_valid():
            form = UserProfileForm(request.POST, request.FILES)
            if form.is_valid():
                username = userCform.cleaned_data['username']
                password = userCform.cleaned_data['password1']
                firstname = userCform.cleaned_data['first_name']
                lastname = userCform.cleaned_data['last_name']
                email = userCform.cleaned_data['email']
                role = form.cleaned_data['role']
                phone_number = form.cleaned_data['phone_number']
                avatar = form.cleaned_data['avatar']
                user = User.objects.create_user(username=username,
                                                first_name=firstname,
                                                last_name=lastname,
                                                password=password,
                                                email=email)
                UserProfile.objects.create(user=user,
                                           role=role,
                                           avatar=avatar,
                                           phone_number=phone_number)
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

@login_required
def create_provider(request):
    return create_associated(request, 'provider')


@login_required
def create_client(request):
    return create_associated(request, 'client')


def create_associated(request, type):
    initial = {'type': type}
    company_id = request.session.get('company_id')
    if company_id is not None:
        initial.setdefault('company', company_id)
        request.session['company_id'] = None
    form = AssociatedCreateForm(initial=initial)
    next = request.GET.get('next', 'list-{}'.format(type))
    if request.method == 'POST':
        form = AssociatedCreateForm(request.POST, request.FILES)
        if form.is_valid():
            associated = form.save()
            request.session['associated_id'] = associated.id
            return redirect(next)
    context = {
        'form': form
    }
    return render(request, 'users/associated_create.html', context)


@login_required
def update_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)
    company_id = request.session.get('company_id')
    if company_id is not None:
        company = get_object_or_404(Company, id=company_id)
        associated.company = company
        request.session['company_id'] = None
    # pass the object as instance in form
    form = AssociatedCreateForm(instance=associated)

    if request.method == 'POST':
        # pass the object as instance in form
        form = AssociatedCreateForm(
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
    context = {
        'form': form
    }

    return render(request, 'users/associated_update.html', context)


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
            request.session['company_id'] = company.id
            return redirect(next)
    context = {
        'form': form
    }
    return render(request, 'users/company_create.html', context)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyCreateForm
    template_name = 'users/company_create.html'
    success_url = reverse_lazy('list-company')


@login_required
def select_company(request):
    if request.method == 'POST':
        next = request.GET.get('next', 'list-company')
        company = get_object_or_404(Company, id=request.POST.get('id'))
        request.session['company_id'] = company.id
        return redirect(next)
    companies = Company.objects.filter(active=True).order_by("-created_date")
    return render(request, 'users/company_select.html', {'companies': companies})


@login_required
def list_company(request):
    companies = Company.objects.filter(active=True).order_by("-created_date")
    for company in companies:
        last_order = Order.objects.filter(
            associated__company=company).order_by("-created_date").first()
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
