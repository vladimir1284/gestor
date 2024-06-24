from django.urls import include
from django.urls import path

from .views import category
from .views import expense
from .views import image
from .views import invoice
from .views import labor
from .views import order
from .views import payment
from .views import service
from .views import sms
from .views import storage
from .views import transaction
from services.tools.init_temps import init_temps
from services.views.order.order_status import update_order_status
from services.views.order.print_outstock import order_print_outstock_trans
from services.views.order_decline_reazon import order_decline_reazon
from services.views.order_flow.contact_form import lessee_form
from services.views.order_flow.contract_client_signature import contact_create_handwriting
from services.views.order_flow.contract_client_signature import contract_client_use_old_sign
from services.views.order_flow.contract_end import process_ended_page
from services.views.order_flow.contract_view_conditions import \
    contact_view_conditions
from services.views.order_flow.create_order_contract import \
    create_order_contact
from services.views.order_flow.fast_orders import fast_order_create
from services.views.order_flow.fast_orders import order_quotation
from services.views.order_flow.fast_orders import parts_sale
from services.views.order_flow.generate_url import generate_url
from services.views.order_flow.get_preorder_state import preorder_state
from services.views.order_flow.order_complete import force_order_complete
from services.views.order_flow.order_complete import order_complete
from services.views.order_flow.order_create import create_order
from services.views.order_flow.select_client import select_client
from services.views.order_flow.select_lessee import select_lessee
from services.views.order_flow.select_lessee import select_lessee_trailer
from services.views.order_flow.select_unrented_trailer import \
    select_unrented_trailer
from services.views.order_flow.signature import create_handwriting
from services.views.order_flow.signature import use_old_sign
from services.views.order_flow.start_flow import select_order_flow
from services.views.order_flow.view_conditions import view_conditions
from services.views.order_flow.view_contract_details import \
    view_contract_details
from services.views.order_payment.order_payment import process_order_payment
from services.views.order_payment.rent_not_client_payment import \
    process_payment_rent_without_client
from services.views.picture_capture import capture_service_picture
from services.views.picture_capture import create_expense_capture_picture
from services.views.picture_capture import update_expense_capture_picture

try:
    init_temps()
except Exception as e:
    print(e)

urlpatterns = [
    # -------------------- APIS --------------------------------
    path("api/", include("services.api.urls")),
    # -------------------- Category ----------------------------
    path(
        "create-category/",
        category.CategoryCreateView.as_view(),
        name="create-service-category",
    ),
    path(
        "update-category/<pk>",
        category.CategoryUpdateView.as_view(),
        name="update-service-category",
    ),
    path(
        "list-category/",
        category.CategoryListView.as_view(),
        name="list-service-category",
    ),
    path(
        "delete-category/<id>", category.delete_category, name="delete-service-category"
    ),
    # -------------------- Transaction ----------------------------
    path(
        "create-transaction/<order_id>/<service_id>",
        transaction.create_transaction,
        name="create-service-transaction",
    ),
    path(
        "update-transaction/<id>",
        transaction.update_transaction,
        name="update-service-transaction",
    ),
    path(
        "detail-transaction/<id>",
        transaction.detail_transaction,
        name="detail-service-transaction",
    ),
    path(
        "delete-transaction/<id>",
        transaction.delete_transaction,
        name="delete-service-transaction",
    ),
    # -------------------- Service ----------------------------
    path("create-service/", service.create_service, name="create-service"),
    path("update-service/<id>", service.update_service, name="update-service"),
    path("detail-service/<id>", service.detail_service, name="detail-service"),
    path("list-service/", service.list_service, name="list-service"),
    path(
        "select-service/<next>/<order_id>",
        service.select_service,
        name="select-service",
    ),
    path(
        "select-service/<next>/<order_id>/<type>",
        service.select_service,
        name="select-service",
    ),
    path(
        "select-new-service/<next>/<order_id>",
        service.select_new_service,
        name="select-new-service",
    ),
    path("delete-service/<id>", service.delete_service, name="delete-service"),
    # -------------------- Order ----------------------------
    path("order-flow/", select_order_flow, name="select-service-order-flow"),
    path("fast_order_create/<id>", fast_order_create, name="fast-order-create"),
    path("parts-sale/", parts_sale, name="parts-sale"),
    path("quotation_order/", order_quotation, name="quotation-order"),
    path("select-client/<id>", select_client, name="select-service-client"),
    path("select-client/", select_client, name="select-service-client"),
    # path("get-vin-plate/", order.get_vin_plate, name="get-vin-plate"),
    path("view-conditions/<id>", view_conditions, name="view-conditions"),
    path("use-old-sign/<id>", use_old_sign, name="use-old-sign"),
    path(
        "contract-client-use-old-sign/<token>",
        contract_client_use_old_sign,
        name="contract-client-use-old-sign",
    ),
    path(
        "view-preorder-state/<preorder_id>",
        preorder_state,
        name="view-preorder-state",
    ),
    path(
        "view-conditions-pdf/<id>",
        order.show_conditions_as_pdf,
        name="view-conditions-pdf",
    ),
    path(
        "trailer-identification-pdf/<id>",
        order.gen_trailer_indentification_pdf,
        name="trailer-identification-pdf",
    ),
    path(
        "client-signature/<id>",
        create_handwriting,
        name="client-service-order-signature",
    ),
    path(
        "process-ended-page/",
        process_ended_page,
        name="process-ended-page",
    ),
    path("select-lessee/", select_lessee, name="select-service-lessee"),
    path(
        "select-lessee-trailer/<id>",
        select_lessee_trailer,
        name="select-service-lessee-trailer",
    ),
    path(
        "view-contract-details/<id>",
        view_contract_details,
        name="view-contract-details",
    ),
    path(
        "select-unrented-trailer/",
        select_unrented_trailer,
        name="select-service-unrented-trailer",
    ),
    path(
        "create-order-contact/",
        create_order_contact,
        name="create-service-order-contact",
    ),
    path(
        "create-order-contact/<id>",
        create_order_contact,
        name="create-service-order-contact",
    ),
    path(
        "generate-order-contact-url/<id>",
        generate_url,
        name="generate-service-order-contact-url",
    ),
    path(
        "contact-form/<token>",
        lessee_form,
        name="service-order-contact-form",
    ),
    path(
        "contact-view-conditions/<token>",
        contact_view_conditions,
        name="contact-view-conditions",
    ),
    path(
        "contact-client-signature/<token>",
        contact_create_handwriting,
        name="contact-client-service-order-signature",
    ),
    path("create-order/<id>", create_order, name="create-service-order"),
    path("update-order/<id>", order.update_order, name="update-service-order"),
    path(
        "detail-order-back/<id>/<back>",
        order.detail_order_back,
        {"msg": ""},
        name="detail-service-order-back",
    ),
    path(
        "detail-order-back/<id>/<back>/<msg>",
        order.detail_order_back,
        name="detail-service-order-back",
    ),
    path(
        "detail-order/<id>",
        order.detail_order,
        {"msg": ""},
        name="detail-service-order",
    ),
    path("detail-order/<id>/<msg>/", order.detail_order, name="detail-service-order"),
    path(
        "order-out-stock-print/<id>",
        order_print_outstock_trans,
        name="service-order-out-stock-print",
    ),
    path(
        "order-send-invoice/<id>",
        order.send_invoice_email,
        name="service-order-send-invoice",
    ),
    path("list-order/", order.list_order, name="list-service-order"),
    path(
        "service-order-on-pos/",
        order.list_order_on_pos,
        name="service-order-on-pos",
    ),
    path(
        "list-terminated-order/",
        order.list_terminated_order,
        name="list-service-order-terminated",
    ),
    path(
        "list-terminated-order/<year>/<month>",
        order.list_terminated_order,
        name="list-service-order-terminated",
    ),
    path(
        "order-decline-reazon/<id>",
        order_decline_reazon,
        name="order-decline-reazon",
    ),
    path(
        "update-order-status/<id>/<status>",
        update_order_status,
        name="update-service-order-status",
    ),
    path(
        "update-order-position/<id>/<status>",
        order.order_end_update_position,
        name="update-order-position",
    ),
    path(
        "order-position-change/<id>",
        order.order_change_position,
        name="order-position-change",
    ),
    path(
        "order-position-change-storage/<id>",
        order.order_change_position_from_storage,
        name="order-position-change-storage",
    ),
    path("send-sms/<order_id>", sms.sendSMS, name="send-sms"),
    # -------------------- Invoice ----------------------------
    path("service-invoice/<id>", invoice.view_invoice, name="service-invoice"),
    path("pdf-invoice/<id>", invoice.generate_invoice, name="pdf-invoice"),
    path("html-invoice/<id>", invoice.html_invoice, name="html-invoice"),
    # -------------------- Labor ----------------------------
    path("service-labor/<id>", labor.view_labor, name="service-labor"),
    path("pdf-labor/<id>", labor.generate_labor, name="pdf-labor"),
    path("html-labor/<id>", labor.html_labor, name="html-labor"),
    # -------------------- Expense ----------------------------
    path("create-expense/<order_id>", expense.create_expense, name="create-expense"),
    path("update-expense/<id>", expense.update_expense, name="update-expense"),
    path("delete-expense/<id>", expense.delete_expense, name="delete-expense"),
    # -------------------- Picture ----------------------------
    path(
        "capture-service-picture/<order_id>",
        capture_service_picture,
        name="capture-service-picture",
    ),
    path(
        "update-expense-capture-picture/<expense_id>",
        update_expense_capture_picture,
        name="update-expense-capture-picture",
    ),
    path(
        "create-expense-capture-picture/<order_id>",
        create_expense_capture_picture,
        name="create-expense-capture-picture",
    ),
    # ----------------- Service Picture -----------------------
    path(
        "new_picture/<int:order_id>",
        image.create_service_pictures,
        name="create-service-pictures",
    ),
    path(
        "share_images/<ids>",
        image.share_service_pictures,
        name="share-service-pictures",
    ),
    path(
        "delete_service_images/<ids>",
        image.delete_service_picture,
        name="delete-service-pictures",
    ),
    # -------------------- Payment ----------------------------
    path(
        "create-payment-category/",
        payment.create_payment_category,
        name="create-payment-category",
    ),
    path(
        "list-payment-category/",
        payment.list_payment_category,
        name="list-payment-category",
    ),
    path(
        "update-payment-category/<id>",
        payment.update_payment_category,
        name="update-payment-category",
    ),
    path(
        "delete-payment-category/<id>",
        payment.delete_payment_category,
        name="delete-payment-category",
    ),
    path(
        "delete-payment/<id>/<int:order_id>",
        payment.delete_payment,
        name="delete-payment",
    ),
    path(
        "process-payment/<int:order_id>",
        process_order_payment,
        name="process-payment",
    ),
    path(
        "process-payment/<int:order_id>/<decline_unsatisfied>",
        process_order_payment,
        name="process-payment",
    ),
    path("pay-debt/<int:client_id>", payment.pay_debt, name="pay-debt"),
    path(
        "update-debt-status/<int:client_id>/<status>",
        payment.update_debt_status,
        name="update-debt-status",
    ),
    path("storage", storage.storage, name="storage-view"),
    path("storage/<tab>", storage.storage, name="storage-view"),
    ################# Order Complete ######################
    path(
        "service-order-complete/<id>",
        order_complete,
        name="service-order-complete",
    ),
    path(
        "service-order-complete/<id>/<decline_unsatisfied>",
        order_complete,
        name="service-order-complete",
    ),
    path(
        "service-order-payment-trailer-without-client/<order_id>",
        process_payment_rent_without_client,
        name="service-order-payment-trailer-without-client",
    ),
    path(
        "service-order-payment-trailer-without-client/<order_id>/<decline_unsatisfied>",
        process_payment_rent_without_client,
        name="service-order-payment-trailer-without-client",
    ),
    path(
        "service-order-complete-forced/<id>",
        force_order_complete,
        name="service-order-complete-forced",
    ),
]
