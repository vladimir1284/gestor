from django.urls import path
from django.contrib.auth import views

from .views import (
    # ---- User -------------
    create_user,
    update_user,
    list_user,
    delete_user,
    # ---- Associated -------
    create_provider,
    create_client,
    list_provider,
    list_client,
    update_associated,
    delete_associated,
    detail_associated,
    # ---- Company -------
    create_company,
    list_company,
    select_company,
    delete_company,
    update_company,
)

urlpatterns = [
    # ----------------------- AUTH -------------------------------
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("password_change/", views.PasswordChangeView.as_view(),
         name="password_change"),
    path("password_change/done/",
         views.PasswordChangeDoneView.as_view(),
         name="password_change_done",
         ),
    path("password_reset/",
         views.PasswordResetView.as_view(),
         name="password_reset"
         ),
    path("password_reset/done/",
         views.PasswordResetDoneView.as_view(),
         name="password_reset_done",
         ),
    path("reset/<uidb64>/<token>/",
         views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm",
         ),
    path("reset/done/",
         views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete",
         ),
    # ----------------------- User -------------------------------
    path('create-user/', create_user, name='create-user'),
    path('update-user/<id>', update_user, name='update-user'),
    path('list-user/', list_user, name='list-user'),
    path('delete-user/<id>', delete_user, name='delete-user'),
    # -------------------- Associated ----------------------------
    path('create-client/', create_client, name='create-client'),
    path('create-provider/', create_provider, name='create-provider'),
    path('update-associated/<id>', update_associated, name='update-associated'),
    path('detail-associated/<id>', detail_associated, name='detail-associated'),
    path('list-provider/', list_provider, name='list-provider'),
    path('list-client/', list_client, name='list-client'),
    path('delete-associated/<id>', delete_associated, name='delete-associated'),
    # ----------------------- Company -------------------------------
    path('select-company/', select_company, name='select-company'),
    path('create-company/', create_company, name='create-company'),
    path('update-company/<id>', update_company, name='update-company'),
    path('list-company/', list_company, name='list-company'),
    path('delete-company/<id>', delete_company, name='delete-company'),
]
