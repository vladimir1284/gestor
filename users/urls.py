from django.contrib.auth import views
from django.urls import path

from .views import create_client
from .views import create_company
from .views import create_provider
from .views import create_user
from .views import create_user_profile
from .views import CustomLoginView
from .views import delete_associated
from .views import delete_company
from .views import delete_user
from .views import detail_associated
from .views import detail_company
from .views import export_contact
from .views import list_client
from .views import list_company
from .views import list_deactivated_client
from .views import list_debtor
from .views import list_provider
from .views import list_user
from .views import select_company
from .views import update_associated
from .views import update_company
from .views import update_user

urlpatterns = [
    # ----------------------- AUTH -------------------------------
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "password_change/", views.PasswordChangeView.as_view(), name="password_change"
    ),
    path(
        "password_change/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # ----------------------- User -------------------------------
    path("create-user/", create_user, name="create-user"),
    path("update-user/<id>", update_user, name="update-user"),
    path("create-user-profile/<id>", create_user_profile,
         name="create-user-profile"),
    path("list-user/", list_user, name="list-user"),
    path("delete-user/<id>", delete_user, name="delete-user"),
    # -------------------- Associated ----------------------------
    path("create-client/", create_client, name="create-client"),
    path("create-provider/", create_provider, name="create-provider"),
    path("update-associated/<id>", update_associated, name="update-associated"),
    path("detail-associated/<id>", detail_associated, name="detail-associated"),
    path("list-provider/", list_provider, name="list-provider"),
    path("list-client/", list_client, name="list-client"),
    path(
        "list-deactivated-client/",
        list_deactivated_client,
        name="list-deactivated-client",
    ),
    path("list-debtor/", list_debtor, name="list-debtor"),
    path("delete-associated/<id>", delete_associated, name="delete-associated"),
    # ----------------------- Company -------------------------------
    path("select-company/", select_company, name="select-company"),
    path("create-company/", create_company, name="create-company"),
    path("update-company/<id>", update_company, name="update-company"),
    path("detail-company/<id>", detail_company, name="detail-company"),
    path("list-company/", list_company, name="list-company"),
    path("delete-company/<id>", delete_company, name="delete-company"),
    path("export-contact/<type>/<id>", export_contact, name="export-contact"),
]
