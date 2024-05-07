from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from template_admin.forms.editor import ListEditorForm
from template_admin.forms.editor import TextEditorForm
from template_admin.models.template_version import TemplateVersion
from template_admin.tools.templates_tools import TT_LIST


@login_required
def template_version_edit(request: HttpRequest, id: int, version: int | None = None):
    template: TemplateVersion = get_object_or_404(TemplateVersion, id=id)
    temp_version = template.version(version)
    if temp_version is None:
        raise Http404(f"Version {version} does not exists.")

    if template.tmp_type == TT_LIST:
        TempForm = ListEditorForm
        TempPath = "templates/templates_list_editor.html"
    else:
        TempForm = TextEditorForm
        TempPath = "templates/templates_text_editor.html"

    initial = {
        "text": temp_version.content,
    }

    if request.method == "POST":
        form = TempForm(request.POST, initial=initial)
        if form.is_valid():
            temp_version.content = form.cleaned_data["text"]
            temp_version.save()
            return redirect("template-list")
    else:
        form = TempForm(initial=initial)

    context = {
        "form": form,
        "template": template,
        "version": temp_version,
        "versions": template.versions_list_date,
        "content": temp_version.content,
    }
    return render(request, TempPath, context)
