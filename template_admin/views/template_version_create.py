from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from template_admin.forms.create_temp_version import CreateTemplateVersionForm
from template_admin.models.template_version import TemplateVersion


@login_required
@atomic
def template_create(request: HttpRequest, id: int | None = None):
    if id is None:
        temp = None
    else:
        temp = TemplateVersion.objects.filter(id=id).last()

    if request.method == "POST":
        form = CreateTemplateVersionForm(request.POST, instance=temp)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.custom = True
            temp.save()
            version = temp.version()
            if version is None:
                version = temp.new_version()
            return redirect("template-version-edit", temp.id, version.version)
    else:
        form = CreateTemplateVersionForm(instance=temp)

    ctx = {
        "title": "New template" if temp is None else "Edit template",
        "form": form,
    }
    return render(request, "templates/templates_create.html", ctx)
