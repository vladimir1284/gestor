from django.urls import path
from .views import (
    # ---- Category -------
    create_category,
    update_category,
    list_category,
    delete_category,
    # ---- Order ----------
    create_order,
    update_order,
    detail_order,
    list_order,
    update_order_status,
    # ---- Transaction ----
    create_transaction,
    create_transaction_new_order,
    update_transaction,
    delete_transaction,
    detail_transaction,
    # ---- Unit ----------
    create_unit,
    list_unit,
    # ---- Product -------
    create_product,
    update_product,
    list_product,
    detail_product,
    select_product,
    select_new_product,
    delete_product,
)


urlpatterns = [
    # -------------------- Category ----------------------------
    path('create-category/', create_category, name='create-category'),
    path('update-category/<id>', update_category, name='update-category'),
    path('list-category/', list_category, name='list-category'),
    path('delete-category/<id>', delete_category, name='delete-category'),
    # -------------------- Order ----------------------------
    path('create-order/', create_order, name='create-order'),
    path('create-order/<product_id>', create_order,
         name='create-order-from-product'),
    path('update-order/<id>', update_order, name='update-order'),
    path('detail-order/<id>', detail_order, name='detail-order'),
    path('list-order/', list_order, name='list-order'),
    path('update-order-status/<id>/<status>',
         update_order_status, name='update-order-status'),
    # -------------------- Transaction ----------------------------
    path('create-transaction/<order_id>/<product_id>',
         create_transaction, name='create-transaction'),
    path('create-transaction-new-order/<product_id>',
         create_transaction_new_order, name='create-transaction-new-order'),
    path('update-transaction/<id>', update_transaction, name='update-transaction'),
    path('detail-transaction/<id>', detail_transaction, name='detail-transaction'),
    path('delete-transaction/<id>', delete_transaction, name='delete-transaction'),
    # -------------------- Unit ----------------------------
    path('create-unit/', create_unit, name='create-unit'),
    path('list-unit/', list_unit, name='list-unit'),
    # -------------------- Product ----------------------------
    path('create-product/', create_product, name='create-product'),
    path('update-product/<id>', update_product, name='update-product'),
    path('detail-product/<id>', detail_product, name='detail-product'),
    path('list-product/', list_product, name='list-product'),
    path('select-product/<next>/<order_id>',
         select_product, name='select-product'),
    path('select-new-product/<next>/<order_id>',
         select_new_product, name='select-new-product'),
    path('delete-product/<id>', delete_product, name='delete-product'),
]
