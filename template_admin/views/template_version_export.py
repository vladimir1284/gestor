import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from template_admin.models.template_version import TemplateVersion
from template_admin.tools.template_version_export import export_template_version


@login_required
def template_version_export(request: HttpRequest, id, version=None):
    temp: TemplateVersion = get_object_or_404(TemplateVersion, id=id)

    data = export_template_version(
        temp, versions=None if version is None else [version]
    )

    jsonData = json.dumps(data)

    resp = HttpResponse(jsonData, content_type="application/json")
    resp["Content-Disposition"] = (
        f'attachment; filename="template_{temp.module}_{temp.template}_{temp.language}.json"'
        if version is None
        else f'attachment; filename="template_{temp.module}_{temp.template}_{temp.language}_v{version}.json"'
    )

    return resp
