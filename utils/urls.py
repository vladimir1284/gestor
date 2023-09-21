from django.urls import path
from .views import list_plate, detail_plate, create_plate, checkout_plate

urlpatterns = [
    path('plates/', list_plate, name='plate-list'),
    path('plates/<int:plate_id>/', detail_plate, name='plate-detail'),
    path('plates_checkout/<int:plate_id>/',
         checkout_plate, name='plate-checkout'),
    path('plates/create/', create_plate, name='plate-create'),
]
