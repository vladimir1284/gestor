from django.urls import path

from .views import (
    # ---- User -------------
    create_user,
    # ---- Associated -------
    create_provider,
    create_client,
    list_provider,
    list_client,
    update_associated,
    delete_associated,
    detail_associated,
)

urlpatterns = [
    # ----------------------- User -------------------------------
    path('create-user/', create_user, name='create-user'),
    # -------------------- Associated ----------------------------
    path('create-client/', create_client, name='create-client'),
    path('create-provider/', create_provider, name='create-provider'),
    path('update-associated/<id>', update_associated, name='update-associated'),
    path('detail-associated/<id>', detail_associated, name='detail-associated'),
    path('list-provider/', list_provider, name='list-provider'),
    path('list-client/', list_client, name='list-client'),
    path('delete-associated/<id>', delete_associated, name='delete-associated'),
]
