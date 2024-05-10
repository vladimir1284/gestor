from django.urls import path

from .permissions import staff_required_view
from .views import calendar
from .views import client
from .views import invoice
from .views import lease
from .views import tracker
from .views import vehicle
from .views.cost import CategoryCreateView
from .views.cost import CategoryListView
from .views.cost import CategoryUpdateView
from .views.cost import create_cost
from .views.cost import delete_category
from .views.cost import delete_cost
from .views.cost import detail_cost
from .views.cost import list_cost
from .views.cost import update_cost
from rent.tools.init_conditions import init_conditions
from rent.views.create_lessee_with_data import create_update_lessee_data
from rent.views.deposit import create_lessee_for_reservation
from rent.views.deposit import create_trailer_reservation
from rent.views.deposit import renovate_trailer_reservation
from rent.views.deposit import reserve_trailer
from rent.views.deposit import trailer_deposit_cancel
from rent.views.deposit import trailer_deposit_conditions
from rent.views.deposit import trailer_deposit_details
from rent.views.deposit import trailer_deposit_pdf
from rent.views.deposit import update_lessee_for_reservation
from rent.views.lease.contract_signing import contract_signing
from rent.views.lease.contract_signing import contract_signing_id
from rent.views.lease.contract_signing import is_contract_cli_complete
from rent.views.lease.update_data_on_contract import update_data_on_contract
from rent.views.trailer_change_pos import trailer_change_position

try:
    init_conditions()
except Exception as e:
    print(e)

urlpatterns = [
    # -------------------- Category ----------------------------
    path(
        "create-category/",
        CategoryCreateView.as_view(),
        name="create-costs-rental-category",
    ),
    path(
        "update-category/<pk>",
        CategoryUpdateView.as_view(),
        name="update-costs-rental-category",
    ),
    path(
        "list-category/", CategoryListView.as_view(), name="list-costs-rental-category"
    ),
    path("delete-category/<id>", delete_category, name="delete-costs-rental-category"),
    # -------------------- Costs ----------------------------
    path("create-cost/", create_cost, name="create-cost-rental"),
    path("update-cost/<id>", update_cost, name="update-cost-rental"),
    path("list-cost/", list_cost, name="list-cost-rental"),
    path("list-cost/<year>/<month>", list_cost, name="list-cost-rental"),
    path("detail-cost/<id>", detail_cost, name="detail-cost-rental"),
    path("delete-cost/<id>", delete_cost, name="delete-cost-rental"),
    # -------------------- Vehicle ----------------------------
    path("create-trailer", vehicle.create_trailer, name="create-trailer"),
    path("list-trailer", vehicle.list_equipment, name="list-trailer"),
    path("select-trailer", vehicle.select_trailer, name="select-trailer"),
    path("update-trailer/<id>", vehicle.update_trailer, name="update-trailer"),
    path("delete-trailer/<id>", vehicle.delete_trailer, name="delete-trailer"),
    path("detail-trailer/<id>", vehicle.detail_trailer, name="detail-trailer"),
    path("select-towit", vehicle.select_towit, name="select-towit"),
    path(
        "reserve-trailer/<trailer_id>",
        reserve_trailer,
        name="reserve-trailer",
    ),
    path(
        "reserve-trailer-update-lessee/<trailer_id>/<lessee_id>",
        update_lessee_for_reservation,
        name="reserve-trailer-update-lessee",
    ),
    path(
        "reserve-trailer-create-lessee/<trailer_id>",
        create_lessee_for_reservation,
        name="reserve-trailer-create-lessee",
    ),
    path(
        "create-trailer-reservation/<trailer_id>/<lessee_id>",
        create_trailer_reservation,
        name="create-trailer-reservation",
    ),
    path(
        "renovate-trailer-reservation/<deposit_id>",
        renovate_trailer_reservation,
        name="renovate-trailer-reservation",
    ),
    path(
        "trailer-deposit-details/<id>",
        trailer_deposit_details,
        name="trailer-deposit-details",
    ),
    path(
        "trailer-deposit-cancel/<id>",
        trailer_deposit_cancel,
        name="trailer-deposit-cancel",
    ),
    path(
        "trailer-deposit-conditions/<token>",
        trailer_deposit_conditions,
        name="trailer-deposit-conditions",
    ),
    path(
        "trailer-deposit-conditions-pdf/<token>",
        trailer_deposit_pdf,
        name="trailer-deposit-conditions-pdf",
    ),
    # -------------------- Tracker ----------------------------
    path(
        "create-tracker/<int:trailer_id>",
        tracker.TrackerCreateView.as_view(),
        name="create-trailer-tracker",
    ),
    path("create-tracker/", tracker.TrackerCreateView.as_view(), name="create-tracker"),
    path(
        "update-tracker/<slug:pk>",
        tracker.TrackerUpdateView.as_view(),
        name="update-tracker",
    ),
    path("delete-tracker/<int:id>", tracker.delete_tracker, name="delete-tracker"),
    path("detail-tracker/<int:id>", tracker.tracker_detail, name="detail-tracker"),
    path("trackers-map/", tracker.trackers, name="trackers-map"),
    path("trackers/", tracker.trackers_table, name="trackers-table"),
    path("tracker-upload", tracker.tracker_upload, name="tracker-upload"),
    # -------------------- Manufacturer ----------------------------
    path("manufacturer-list", vehicle.manufacturer_list, name="manufacturer-list"),
    path(
        "manufacturer-create/", vehicle.manufacturer_create, name="manufacturer-create"
    ),
    path(
        "manufacturer-update/<int:pk>",
        vehicle.manufacturer_update,
        name="manufacturer-update",
    ),
    path(
        "manufacturer-delete/<int:pk>",
        vehicle.manufacturer_delete,
        name="manufacturer-delete",
    ),
    # -------------------- Picture ----------------------------
    path(
        "picture/create/<int:trailer_id>",
        vehicle.trailer_picture_create,
        name="trailer-picture-create",
    ),
    path("share_pictures/<ids>", vehicle.share_pictures, name="share-pictures"),
    path(
        "delete_trailer_pictures/<ids>",
        vehicle.delete_trailer_pictures,
        name="delete-trailer-pictures",
    ),
    path(
        "update_pinned_picture/<int:pk>/",
        vehicle.update_pinned_picture,
        name="update-pinned-picture",
    ),
    # -------------------- Trailer Document ----------------------------
    path(
        "document/create/<int:trailer_id>",
        vehicle.create_document,
        name="trailer-document-create",
    ),
    path(
        "update_trailer_document/<id>",
        vehicle.update_document,
        name="update-trailer-document",
    ),
    path(
        "delete_trailer_document/<id>",
        vehicle.delete_document,
        name="delete-trailer-document",
    ),
    # -------------------- Contracts ----------------------------
    path(
        "create_contract/<int:lessee_id>/<int:trailer_id>/",
        lease.contract_create_view,
        name="create-contract",
    ),
    path(
        "create_contract/<int:lessee_id>/<int:trailer_id>/<int:deposit_id>",
        lease.contract_create_view,
        name="create-contract",
    ),
    path(
        "contract-cli-completed/<int:id>",
        is_contract_cli_complete,
        name="contract-cli-completed",
    ),
    path(
        "contract/<int:id>",
        lease.contract_detail,
        name="detail-contract",
    ),
    path("contract_signing/<id>", contract_signing_id, name="contract-signing"),
    path("contract_signature/<token>", contract_signing, name="contract-signature"),
    path("contract_pdf/<int:id>", lease.contract_pdf, name="contract-signed"),
    path("contracts/", lease.contracts, name="contracts"),
    path(
        "update_contract/<slug:pk>",
        lease.ContractUpdateView.as_view(),
        name="update-contract",
    ),
    path(
        "update_contract_stage/<slug:id>/<stage>",
        lease.update_contract_stage,
        name="update-contract-stage",
    ),
    path(
        "capture_signature/<str:position>/<str:token>",
        lease.create_handwriting,
        name="capture-signature",
    ),
    path(
        "ext_capture_signature/<str:position>/<str:token>",
        lease.create_handwriting,
        {
            "external": True,
        },
        name="ext-capture-signature",
    ),
    path("adjust_deposit/<id>/", lease.adjust_end_deposit, name="adjust-deposit"),
    path(
        "create_document_on_ended_contract/<id>/",
        lease.create_document_on_ended_contract,
        name="create-document-on-ended-contract",
    ),
    path(
        "delete_document_on_ended_contract/<id>/",
        lease.delete_document_on_ended_contract,
        name="delete-document-on-ended-contract",
    ),
    # -------------------- Lessee ----------------------------
    path("select_lessee/<int:trailer_id>/", lease.select_lessee, name="select-lessee"),
    path(
        "update_lesee/<int:trailer_id>/<int:lessee_id>/",
        lease.update_lessee,
        name="update-lessee",
    ),
    path(
        "update_lesee/<int:trailer_id>/<int:lessee_id>/<int:deposit_id>",
        lease.update_lessee,
        name="update-lessee",
    ),
    path("create_lesee/<int:trailer_id>/", lease.update_lessee, name="create-lessee"),
    path(
        "create_lessee_data/<int:trailer_id>/<int:lessee_id>/",
        lease.create_lessee_data,
        name="update-lessee-data",
    ),
    path(
        "create_lessee_data/<int:trailer_id>/<int:lessee_id>/<int:deposit_id>",
        lease.create_lessee_data,
        name="update-lessee-data",
    ),
    path(
        "client_create_lessee_data/<token>/",
        lease.client_create_lessee_data,
        name="client-create-lessee-data",
    ),
    path(
        "create_lessee_contact/<int:trailer_id>/",
        lease.create_lessee_contact,
        name="create-lessee-contact",
    ),
    path(
        "lessee_data_form/<str:token>/",
        create_update_lessee_data,
        name="lessee_data_form",
    ),
    path(
        "generate_lessee_url/<trailer_id>/<associated_id>/",
        lease.generate_url,
        name="generate-lessee-url",
    ),
    path(
        "lessee_form/<token>",
        lease.lessee_form,
        name="lessee-form",
    ),
    path(
        "lessee_form_completed/",
        lease.lessee_form_ok,
        name="lessee-form-completed",
    ),
    path(
        "update_lessee_data/<slug:pk>",
        lease.LeseeDataUpdateView.as_view(),
        name="update-lessee-data",
    ),
    path(
        "update_data_on_contract/<id>",
        update_data_on_contract,
        name="update-data-on-contract",
    ),
    # -------------------- Inspection ----------------------------
    path(
        "create_inspection/<lease_id>/",
        lease.create_inspection,
        name="create-inspection",
    ),
    path("update_inspection/<id>/", lease.update_inspection, name="update-inspection"),
    path("update_tires/<inspection_id>/", lease.update_tires, name="update-tires"),
    # -------------------- Calendar ----------------------------
    path("api_occurrences/", calendar.api_occurrences, name="api-occurrences"),
    path("calendar/", calendar.calendar_week, name="calendar"),
    # -------------------- Client ----------------------------
    path("toggle_alarm/<lease_id>/", client.toggle_alarm, name="toggle-alarm"),
    path("client_detail/<id>/", client.client_detail, name="client-detail"),
    path("client_list/", client.client_list, name="client-list"),
    path("payment/<client_id>/", client.payment, name="rental-payment"),
    path("detail_payment/<id>/", client.detail_payment, name="detail-payment"),
    path("revert_payment/<id>", client.revert_payment, name="revert-payment"),
    # -------------------- Invoice ----------------------------
    path(
        "invoice/<lease_id>/<date>/<str:paid>", invoice.invoice, name="rental-invoice"
    ),
    path(
        "pdf-invoice/<lease_id>/<date>/<str:paid>",
        invoice.generate_invoice,
        name="rental-pdf-invoice",
    ),
    path(
        "send_mail/<lease_id>/<date>/<str:paid>",
        invoice.send_invoice,
        name="rental-send-invoice",
    ),
    # -------------------- Lease Document ----------------------------
    path(
        "lease_document/create/<int:lease_id>",
        lease.create_document,
        name="lease-document-create",
    ),
    path(
        "update_lease_document/<id>",
        lease.update_document,
        name="update-lease-document",
    ),
    path(
        "delete_lease_document/<id>",
        lease.delete_document,
        name="delete-lease-document",
    ),
    # -------------------- Lease Deposit ----------------------------
    path(
        "lease_deposit/create/<int:lease_id>",
        lease.create_deposit,
        name="lease-deposit-create",
    ),
    path(
        "delete_lease_deposit/<id>", lease.delete_deposit, name="delete-lease-deposit"
    ),
    # -------------------- Lease ----------------------------
    path("update_lease/<id>", lease.update_lease, name="update-lease"),
    # -------------------- Due ----------------------------
    path("create_due/<int:lease_id>/<str:date>", lease.create_due, name="create-due"),
    path("update_due/<id>", lease.update_due, name="update-due"),
    # -------------------- Permissions ----------------------------
    path("staff_required/", staff_required_view, name="staff_required"),
    # -------------------- Note ----------------------------
    path("create_note/<int:contract_id>", client.create_note, name="create-note"),
    path("delete_note/<id>", client.delete_note, name="delete-note"),
    path(
        "deactivate_reminder/<id>",
        client.deactivate_reminder,
        name="deactivate-reminder",
    ),
    # -------------------- Cost ----------------------------
    path(
        "change_trailer_pos/<id>",
        trailer_change_position,
        name="change-trailer-pos",
    ),
]
