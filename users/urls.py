from django.urls import path

from .views import login_page, logout_page, create_user

urlpatterns = [
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout'),
    path('create-user/', create_user, name='create-user'),
]