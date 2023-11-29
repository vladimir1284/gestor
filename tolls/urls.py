from django.urls import path
from .views import list_toll, create_toll, update_toll, delete_toll

urlpatterns = [
    path('list-toll/', list_toll, name='list-toll'),
    path('list-toll/<id>/', list_toll, name='list-toll'),
    path('create-toll/', create_toll, name='create-toll'),
    path('create-toll/<int:plate>/', create_toll, name='create-toll'),
    path('create-toll/<int:plate>/<int:contract>/', create_toll, name='create-toll'),
    path('update-toll/<int:id>/', update_toll, name='update-toll'),
    path('delete-toll/<int:id>/', delete_toll, name='delete-toll')
]