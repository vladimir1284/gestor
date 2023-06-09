from django.urls import path
from .views import (
    # ---- Equipment -------
    list_equipment,
    select_equipment,
    select_equipment_type,
    # ---- Trailer ----
    create_trailer,
    update_trailer,
    delete_trailer,
    detail_trailer,
    # ------ Vehicle ------
    create_vehicle,
    update_vehicle,
    delete_vehicle,
    detail_vehicle,
)


urlpatterns = [
    # -------------------- Equipment ----------------------------
    path('list-equipment/', list_equipment, name='list-equipment'),
    path('select-equipment', select_equipment, name='select-equipment'),
    path('select-type/', select_equipment_type, name='select-equipment-type'),
    # -------------------- Trailer ----------------------------
    path('create-trailer', create_trailer, name='create-old-trailer'),
    path('update-trailer/<id>', update_trailer, name='update-old-trailer'),
    path('delete-trailer/<id>', delete_trailer, name='delete-old-trailer'),
    path('detail-trailer/<id>', detail_trailer, name='detail-old-trailer'),
    # -------------------- Vehicle ----------------------------
    path('create-vehicle', create_vehicle, name='create-vehicle'),
    path('update-vehicle/<id>', update_vehicle, name='update-vehicle'),
    path('delete-vehicle/<id>', delete_vehicle, name='delete-vehicle'),
    path('detail-vehicle/<id>', detail_vehicle, name='detail-vehicle'),
]
