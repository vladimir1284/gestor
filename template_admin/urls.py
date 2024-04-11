from django.urls import path

from template_admin.views.template_edit import template_edit
from template_admin.views.template_list import template_list


urlpatterns = [
    path("template-list", template_list, name="template-list"),
    path("template-edit/<id>", template_edit, name="template-edit"),
]
