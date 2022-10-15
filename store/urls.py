from django.urls import path
from .views import (
    create_unit, 
    create_category, 
    create_product,
    create_associated,
)


urlpatterns = [
    path('create-unit/', create_unit, name='create-unit'),
    path('create-associated/', create_associated, name='create-associated'),
    path('create-product/', create_product, name='create-product'),
    path('create-category/', create_category, name='create-category'),
]
