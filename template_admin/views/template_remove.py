from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect

from template_admin.models.template_version import TemplateVersion


@login_required
def template_remove(request: HttpRequest, id):
    TemplateVersion.objects.filter(id=id).delete()
    return redirect("template-list", True)
