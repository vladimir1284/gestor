from datetime import datetime

from django.db.transaction import atomic
from django.shortcuts import get_object_or_404

from template_admin.models.template_content_version import TemplateContentVersion
from template_admin.models.template_version import TemplateVersion


def import_template_version_content(temp: TemplateVersion, data: dict):
    tvc = temp.version(data["version"])

    if tvc is None:
        tvc = TemplateContentVersion.objects.create(
            template=temp,
            version=data["version"],
            created_date=datetime.strptime(data["created_date"], "%m/%d/%Y"),
            content=data["content"],
        )
    else:
        tvc.version = data["version"]
        tvc.created_date = datetime.strptime(data["created_date"], "%m/%d/%Y")
        tvc.content = data["content"]
        tvc.save()

    tvc.set_mapped_options(data["options"])
    for dep in data["dependencies"]:
        temp = TemplateVersion.objects.filter(
            module=dep["module"],
            template=dep["template"],
            language=dep["language"],
            tmp_type=dep["tmp_type"],
        ).last()
        if temp is not None:
            import_template_version(dep, temp.id)
        else:
            import_template_version(dep)


@atomic
def import_template_version(data: dict, id: int | None = None):
    if id is None:
        temp = TemplateVersion.objects.create(
            module=data["module"],
            template=data["template"],
            language=data["language"],
            tmp_type=data["tmp_type"],
            custom=data["custom"],
        )
    else:
        temp = get_object_or_404(TemplateVersion, id=id)
        if temp.custom:
            temp.module = data["module"]
            temp.template = data["template"]
            temp.language = data["language"]
            temp.tmp_type = data["tmp_type"]
            temp.save()

    for v in data["versions"]:
        import_template_version_content(temp, v)
