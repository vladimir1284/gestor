from django.urls import path

from .views import create_contract_toll
from .views import create_toll
from .views import delete_toll
from .views import list_toll
from .views import update_toll

urlpatterns = [
    path("list-toll/", list_toll, name="list-toll"),
    path("list-toll/<id>/", list_toll, name="list-toll"),
    path("create-toll/", create_toll, name="create-toll"),
    path("create-toll/<int:plate>/", create_toll, name="create-toll"),
    path("create-toll/<int:plate>/<int:contract>/", create_toll, name="create-toll"),
    path(
        "create-contract-toll/<int:contract>/",
        create_contract_toll,
        name="create-contract-toll",
    ),
    path("update-toll/<int:id>/", update_toll, name="update-toll"),
    path("delete-toll/<int:id>/", delete_toll, name="delete-toll"),
]

