from django.urls import path

from .views import (
    # ---- login ------------
    login_page,
    logout_page,
    # ---- User -------------
    create_user,
    # ---- Associated -------
    create_provider,
    list_provider,
    list_client,
    update_associated,
)

urlpatterns = [
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout'),
    # ----------------------- User -------------------------------
    path('create-user/', create_user, name='create-user'),
    # -------------------- Associated ----------------------------
    path('create-associated/', create_provider, name='create-associated'),
    path('update-associated/<id>', update_associated, name='update-associated'),
    path('list-providers/', list_provider, name='list-providers'),
    path('list-client/', list_client, name='list-client'),
]
