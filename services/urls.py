from django.urls import path
from .views import (
    # ---- Category -------
    create_category,
    update_category,
    list_category,
    delete_category,
    # ---- Transaction ----
    create_transaction,
    update_transaction,
    delete_transaction,
    detail_transaction,
)


urlpatterns = [
    # -------------------- Category ----------------------------
    path('create-category/', create_category, name='create-service-category'),
    path('update-category/<id>', update_category,
         name='update-service-category'),
    path('list-category/', list_category, name='list-service-category'),
    path('delete-category/<id>', delete_category,
         name='delete-service-category'),
    # -------------------- Transaction ----------------------------
    path('create-transaction/<order_id>/<product_id>',
         create_transaction, name='create-service-transaction'),
    path('update-transaction/<id>', update_transaction,
         name='update-service-transaction'),
    path('detail-transaction/<id>', detail_transaction,
         name='detail-service-transaction'),
    path('delete-transaction/<id>', delete_transaction,
         name='delete-service-transaction'),
]
