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
    delete_service,
    # ---- Order ----------
    create_order,
    select_client,
    update_order,
    detail_order,
    list_order,
    update_order_status,
    view_invoice,
    generate_invoice,
    html_invoice,
    # ---- Expense ----------
    create_expense,
    update_expense,
    delete_expense,
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
    # -------------------- Order ----------------------------
    path('select-client/', select_client, name='select-service-client'),
    path('create-order/', create_order, name='create-service-order'),
    path('update-order/<id>', update_order, name='update-service-order'),
    path('detail-order/<id>', detail_order, name='detail-service-order'),
    path('service-invoice/<id>', view_invoice, name='service-invoice'),
    path('pdf-invoice/<id>', generate_invoice, name='pdf-invoice'),
    path('html-invoice/<id>', html_invoice, name='html-invoice'),
    path('list-order/', list_order, name='list-service-order'),
    path('update-order-status/<id>/<status>',
         update_order_status, name='update-service-order-status'),
    # -------------------- Expense ----------------------------
    path('create-expense/<order_id>', create_expense, name='create-expense'),
    path('update-expense/<id>', update_expense, name='update-expense'),
    path('delete-expense/<id>', delete_expense, name='delete-expense'),
]
