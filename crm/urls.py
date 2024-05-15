from django.urls import path
from .views import handle_incoming_call

urlpatterns = [
    path("handle-call", handle_incoming_call, name="registro"),
]