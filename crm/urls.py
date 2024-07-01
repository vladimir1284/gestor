from django.urls import path
from .views import crm_view, twilio_views

urlpatterns = [
    path("handle-call", twilio_views.handle_call, name="registro"),
    path("registro", twilio_views.registro, name="registro-llamadas"),
    path("delete_register/<id>", crm_view.flagged_call_view, name="borrar_del_registro"),
    path("create-client-crm/<id>", crm_view.create_associated, name="created_associated_crm" )
]