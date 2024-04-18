from django.urls import path

from services.views.order_flow.contact_form import lessee_form
from services.views.order_flow.contract_client_signature import (
    contact_create_handwriting,
)
from services.views.order_flow.contract_client_signature import (
    contract_client_use_old_sign,
)
from services.views.order_flow.contract_end import process_ended_page
from services.views.order_flow.contract_view_conditions import contact_view_conditions

urlpatterns = [
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
    path(
        "contract-client-use-old-sign/<token>",
        contract_client_use_old_sign,
        name="contract-client-use-old-sign",
    ),
    path(
        "process-ended-page/",
        process_ended_page,
        name="process-ended-page",
    ),
]
