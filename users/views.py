from django.shortcuts import render, redirect, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required

from .forms import LoginForm, UserProfileForm, UserCreateForm
from .models import User, UserProfile


def login_page(request):
    forms = LoginForm()
    if request.method == 'POST':
        forms = LoginForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(request.GET['next'])
    context = {'form': forms}
    return render(request, 'users/login.html', context)


def logout_page(request):
    logout(request)
    return redirect('login')


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
