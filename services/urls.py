from django.urls import path
from .views import (
    category,
    expense,
    image,
    invoice,
    order,
    payment,
    service,
    sms,
    transaction,
    labor
)


urlpatterns = [
    # -------------------- Category ----------------------------
    path('create-category/', category.CategoryCreateView.as_view(),
         name='create-service-category'),
    path('update-category/<pk>', category.CategoryUpdateView.as_view(),
         name='update-service-category'),
    path('list-category/', category.CategoryListView.as_view(),
         name='list-service-category'),
    path('delete-category/<id>', category.delete_category,
         name='delete-service-category'),
    # -------------------- Transaction ----------------------------
    path('create-transaction/<order_id>/<service_id>',
         transaction.create_transaction, name='create-service-transaction'),
    path('update-transaction/<id>', transaction.update_transaction,
         name='update-service-transaction'),
    path('detail-transaction/<id>', transaction.detail_transaction,
         name='detail-service-transaction'),
    path('delete-transaction/<id>', transaction.delete_transaction,
         name='delete-service-transaction'),
    # -------------------- Service ----------------------------
    path('create-service/', service.create_service, name='create-service'),
    path('update-service/<id>', service.update_service, name='update-service'),
    path('detail-service/<id>', service.detail_service, name='detail-service'),
    path('list-service/', service.list_service, name='list-service'),
    path('select-service/<next>/<order_id>',
         service.select_service, name='select-service'),
    path('select-new-service/<next>/<order_id>',
         service.select_new_service, name='select-new-service'),
    path('delete-service/<id>', service.delete_service, name='delete-service'),
    # -------------------- Order ----------------------------
    path('select-client/', order.select_client, name='select-service-client'),
    path('create-order/', order.create_order, name='create-service-order'),
    path('update-order/<id>', order.update_order, name='update-service-order'),
    path('detail-order/<id>', order.detail_order, name='detail-service-order'),
    path('list-order/', order.list_order, name='list-service-order'),
    path('list-terminated-order/', order.list_terminated_order,
         name='list-service-order-terminated'),
    path('update-order-status/<id>/<status>',
         order.update_order_status, name='update-service-order-status'),
    path('send-sms/<order_id>', sms.sendSMS, name='send-sms'),
    # -------------------- Invoice ----------------------------
    path('service-invoice/<id>', invoice.view_invoice, name='service-invoice'),
    path('pdf-invoice/<id>', invoice.generate_invoice, name='pdf-invoice'),
    path('html-invoice/<id>', invoice.html_invoice, name='html-invoice'),
    # -------------------- Labor ----------------------------
    path('service-labor/<id>', labor.view_labor, name='service-labor'),
    path('pdf-labor/<id>', labor.generate_labor, name='pdf-labor'),
    path('html-labor/<id>', labor.html_labor, name='html-labor'),
    # -------------------- Expense ----------------------------
    path('create-expense/<order_id>',
         expense.create_expense, name='create-expense'),
    path('update-expense/<id>', expense.update_expense, name='update-expense'),
    path('delete-expense/<id>', expense.delete_expense, name='delete-expense'),
    # ----------------- Service Picture -----------------------
    path('new_picture/<int:order_id>',  image.create_service_pictures,
         name='create-service-pictures'),
    path('share_images/<ids>',  image.share_service_pictures,
         name='share-service-pictures'),
    path('delete_service_images/<ids>',  image.delete_service_picture,
         name='delete-service-pictures'),
    # -------------------- Payment ----------------------------
    path('create-payment-category/',
         payment.create_payment_category, name='create-payment-category'),
    path('list-payment-category/', payment.list_payment_category,
         name='list-payment-category'),
    path('update-payment-category/<id>',
         payment.update_payment_category, name='update-payment-category'),
    path('delete-payment-category/<id>',
         payment.delete_payment_category, name='delete-payment-category'),
    path('delete-payment/<id>/<int:order_id>',
         payment.delete_payment, name='delete-payment'),
    path('process-payment/<int:order_id>',
         payment.process_payment, name='process-payment'),
    path('pay-debt/<int:client_id>',
         payment.pay_debt, name='pay-debt'),
    path('update-debt-status/<int:client_id>/<status>',
         payment.update_debt_status, name='update-debt-status'),

]
