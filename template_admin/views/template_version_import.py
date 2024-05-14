import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render

from template_admin.forms.upload_json import UploadJsonForm
from template_admin.tools.template_version_import import import_template_version


@login_required
def template_version_import(
    request: HttpRequest, id: int | None = None, custom: bool = False
):
    if request.method == "POST":
        form = UploadJsonForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            jsonData = ""
            for c in file.chunks():
                jsonData += c.decode()

            data = json.loads(jsonData)
            import_template_version(data, id)

            if custom == True or custom == "True":
                return redirect("template-list", True)
            return redirect("template-list")
    else:
        form = UploadJsonForm()

    ctx = {
        "title": "Import template",
        "form": form,
    }
    return render(request, "templates/templates_create.html", ctx)
