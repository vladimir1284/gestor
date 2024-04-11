from django.http import HttpRequest
from django.shortcuts import render

from template_admin.models.template import Template


def template_list(request: HttpRequest):
    templates = Template.objects.all()

    context = {
        "templates": templates,
    }
    return render(request, "templates/templates_list.html", context)
