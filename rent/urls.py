from django.urls import path
from .views import (
    # ---- Trailer ----
    list_equipment,
    create_trailer,
    update_trailer,
    delete_trailer,
    detail_trailer,
)


urlpatterns = [
    # -------------------- Trailer ----------------------------
    path('create-trailer', create_trailer, name='create-trailer'),
    path('list-trailer', list_equipment, name='list-trailer'),
    path('update-trailer/<id>', update_trailer, name='update-trailer'),
    path('delete-trailer/<id>', delete_trailer, name='delete-trailer'),
    path('detail-trailer/<id>', detail_trailer, name='detail-trailer'),
]
