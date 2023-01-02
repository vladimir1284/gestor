from django.urls import path
from .views import (
    # ---- Category -------
    CategoryListView,
    delete_category,
    CategoryUpdateView,
    CategoryCreateView,
    # ---- Costs ----------
)


urlpatterns = [
    # -------------------- Category ----------------------------
    path('create-category/', CategoryCreateView.as_view(),
         name='create-costs-category'),
    path('update-category/<pk>', CategoryUpdateView.as_view(),
         name='update-costs-category'),
    path('list-category/', CategoryListView.as_view(), name='list-costs-category'),
    path('delete-category/<id>', delete_category, name='delete-costs-category'),
    # -------------------- Costs ----------------------------
]
