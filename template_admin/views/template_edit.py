from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from template_admin.forms.editor import ListEditorForm
from template_admin.forms.editor import TextEditorForm
from template_admin.models.template import Template
from template_admin.models.template import TT_LIST


def template_edit(request: HttpRequest, id):
    template: Template = get_object_or_404(Template, id=id)

    if template.tmp_type == TT_LIST:
        TempForm = ListEditorForm
        TempPath = "templates/templates_list_editor.html"
    else:
        TempForm = TextEditorForm
        TempPath = "templates/templates_text_editor.html"

    initial = {
        "text": template.content,
    }

    if request.method == "POST":
        form = TempForm(request.POST, initial=initial)
        if form.is_valid():
            template.content = form.cleaned_data["text"]
            template.save()
            return redirect("template-list")
    else:
        form = TempForm(initial=initial)

    context = {
        "form": form,
        "template": template,
        "content": template.content,
    }
    return render(request, TempPath, context)
