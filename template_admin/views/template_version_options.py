import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from template_admin.models.template_version import TemplateVersion
from template_admin.views.template_edit import HttpRequest


def template_version_options(request: HttpRequest, id: int, version: int):
    template: TemplateVersion = get_object_or_404(TemplateVersion, id=id)

    if request.method == "POST":
        data = request.POST.get("data", None)
        print(data)
        if data:
            data = json.loads(data)
            print(data)
            template.set_mapped_options(version, data)

    options = template.get_mapped_options(version)
    if options is None:
        return JsonResponse({})
    return JsonResponse(options)
