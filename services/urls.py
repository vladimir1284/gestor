from django.urls import path
from .views import (
    # ---- Category -------
    CategoryListView,
    delete_category,
    CategoryUpdateView,
    CategoryCreateView,
    # ---- Transaction ----
    create_transaction,
    update_transaction,
    delete_transaction,
    detail_transaction,
    # ------ Service ------
    create_service,
    update_service,
    detail_service,
    list_service,
    select_service,
    select_new_service,
    delete_service
)


urlpatterns = [
    # -------------------- Category ----------------------------
    path('create-category/', CategoryCreateView.as_view(),
         name='create-service-category'),
    path('update-category/<pk>', CategoryUpdateView.as_view(),
         name='update-service-category'),
    path('list-category/', CategoryListView.as_view(),
         name='list-service-category'),
    path('delete-category/<id>', delete_category,
         name='delete-service-category'),
    # -------------------- Transaction ----------------------------
    path('create-transaction/<order_id>/<service_id>',
         create_transaction, name='create-service-transaction'),
    path('update-transaction/<id>', update_transaction,
         name='update-service-transaction'),
    path('detail-transaction/<id>', detail_transaction,
         name='detail-service-transaction'),
    path('delete-transaction/<id>', delete_transaction,
         name='delete-service-transaction'),
    # -------------------- Service ----------------------------
    path('create-service/', create_service, name='create-service'),
    path('update-service/<id>', update_service, name='update-service'),
    path('detail-service/<id>', detail_service, name='detail-service'),
    path('list-service/', list_service, name='list-service'),
    path('select-service/<next>/<order_id>',
         select_service, name='select-service'),
    path('select-new-service/<next>/<order_id>',
         select_new_service, name='select-new-service'),
    path('delete-service/<id>', delete_service, name='delete-service'),
]
