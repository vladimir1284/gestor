from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from template_admin.forms.editor import EditorForm
from template_admin.models.template import Template


def template_edit(request: HttpRequest, id):
    template: Template = get_object_or_404(Template, id=id)
    initial = {
        "text": template.content,
    }

    if request.method == "POST":
        form = EditorForm(request.POST, initial=initial)
        if form.is_valid():
            template.content = form.cleaned_data["text"]
            template.save()
            return redirect("template-list")
    else:
        form = EditorForm(initial=initial)

    context = {
        "form": form,
        "template": template,
        "content": template.content,
    }
    return render(request, "templates/templates_editor.html", context)
