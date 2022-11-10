from django.urls import path
from .views import (
    create_unit,
    create_category,
    create_product,
    create_associated,
    create_order,
    list_unit,
    list_category,
    list_product,
    update_category,
    delete_category,
)


urlpatterns = [
    path('create-unit/', create_unit, name='create-unit'),
    path('create-associated/', create_associated, name='create-associated'),
    path('create-product/', create_product, name='create-product'),
    path('create-category/', create_category, name='create-category'),
    path('create-order/', create_order, name='create-order'),
    path('list-unit/', list_unit, name='list-unit'),
    path('list-category/', list_category, name='list-category'),
    path('list-product/', list_product, name='list-product'),
    path('update-category/<id>', update_category, name='update-category'),
    path('delete-category/<id>', delete_category, name='delete-category'),
]
