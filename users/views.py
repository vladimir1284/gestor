from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm, UserProfileForm
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
                return redirect('dashboard')
    context = {'form': forms}
    return render(request, 'users/login.html', context)


def logout_page(request):
    logout(request)
    return redirect('login')


def create_user(request):
    if not request.user.profile_user.role <= 1:
        return redirect('/login/?next=%s' % request.path)
    forms = UserProfileForm()
    if request.method == 'POST':
        forms = UserProfileForm(request.POST)
        if forms.is_valid():
            firstname = forms.cleaned_data['first_name']
            lastname = forms.cleaned_data['last_name']
            role = forms.cleaned_data['role']
            avatar = forms.cleaned_data['avatar']
            email = forms.cleaned_data['email']
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']
            retype_password = forms.cleaned_data['retype_password']
            if password == retype_password:
                user = User.objects.create_user(username=username, 
                                                first_name = firstname,
                                                last_name = lastname,
                                                password=password, 
                                                email=email, 
                                                is_supplier=True)
                UserProfile.objects.create(user=user, role=role, avatar=avatar)
                return redirect('supplier-list')
    context = {
        'form': forms
    }
    return render(request, 'users/addUser.html', context)
