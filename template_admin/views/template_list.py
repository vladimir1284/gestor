from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from template_admin.models.template import Template
from template_admin.models.template_version import TemplateVersion


@login_required
def template_list(request: HttpRequest):
    templates = Template.objects.all()
    templates_version = TemplateVersion.objects.all()

    context = {
        "templates": templates,
        "templates_version": templates_version,
    }
    return render(request, "templates/templates_list.html", context)
