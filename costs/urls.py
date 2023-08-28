from django.urls import path
from .views import (
    # ---- Category -------
    CategoryListView,
    delete_category,
    CategoryUpdateView,
    CategoryCreateView,
    # ---- Costs ----------
    create_cost,
    update_cost,
    list_cost,
    delete_cost,
    detail_cost
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
    path('create-cost/', create_cost, name='create-cost'),
    path('update-cost/<id>', update_cost, name='update-cost'),
    path('list-cost/', list_cost, name='list-cost'),
    path('list-cost/<year>/<month>', list_cost, name='list-cost'),
    path('detail-cost/<id>', detail_cost, name='detail-cost'),
    path('delete-cost/<id>', delete_cost, name='delete-cost'),
]
