from django.urls import path
from .views import *

urlpatterns = [
    path("handle-call", handle_call, name="registro"),
    path("registro", registro, name="registro-llamadas")
]