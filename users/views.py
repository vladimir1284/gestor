import os
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    HttpResponseRedirect)
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import permission_required, login_required

from .forms import (
    UserProfileForm,
    UserCreateForm,
    AssociatedCreateForm,
)

from .models import (
    User,
    UserProfile,
    Associated,
)


@permission_required('auth.user.can_add_user')
def create_user(request):
    forms = UserProfileForm()
    userCform = UserCreateForm()
    if request.method == 'POST':
        userCform = UserCreateForm(request.POST)
        if userCform.is_valid():
            forms = UserProfileForm(request.POST, request.FILES)
            print(forms)
            if forms.is_valid():
                username = userCform.cleaned_data['username']
                password = userCform.cleaned_data['password1']
                firstname = userCform.cleaned_data['first_name']
                lastname = userCform.cleaned_data['last_name']
                email = userCform.cleaned_data['email']
                role = forms.cleaned_data['role']
                phone_number = forms.cleaned_data['phone_number']
                avatar = forms.cleaned_data['avatar']
                user = User.objects.create_user(username=username,
                                                first_name=firstname,
                                                last_name=lastname,
                                                password=password,
                                                email=email)
                UserProfile.objects.create(user=user,
                                           role=role,
                                           avatar=avatar,
                                           phone_number=phone_number)
                return redirect('/')
    context = {
        'form': forms,
        'user_form': userCform
    }
    return render(request, 'users/addUser.html', context)

# -------------------- Associated ----------------------------


@login_required
def create_provider(request):
    return create_associated(request, 'provider')


def create_associated(request, type):
    initial = {'type': type}
    if request.method == 'GET':
        request.session['previous'] = request.META.get('HTTP_REFERER', '/')
    form = AssociatedCreateForm(initial=initial)
    if request.method == 'POST':
        form = AssociatedCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.session['previous'])
    context = {
        'form': form
    }
    return render(request, 'users/addAssociated.html', context)


@login_required
def update_associated(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Associated, id=id)

    # pass the object as instance in form
    form = AssociatedCreateForm(request.POST or None,
                                request.FILES or None, instance=obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        if os.path.exists(obj.icon.path):
            os.remove(obj.icon.path)
        form.save()
        return redirect('list-category')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'users/addAssociated.html', context)


@login_required
def list_provider(request):
    return list_associated(request, 'supplier')


@login_required
def list_client(request):
    return list_associated(request, 'client')


@login_required
def detail_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)
    return render(request, 'users/associated_detail.html', {'associated': associated})


def list_associated(request, type):
    associateds = Associated.objects.filter(type=type)
    return render(request, 'users/associated_list.html', {'associateds': associateds})
