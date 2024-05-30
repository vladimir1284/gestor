from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from template_admin.models.template_version import TemplateVersion


@login_required
def template_version_new(request: HttpRequest, id: int):
    template: TemplateVersion = get_object_or_404(TemplateVersion, id=id)
    version = template.new_version()
    return redirect("template-version-edit", id, version.version)
