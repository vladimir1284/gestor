import re

from template_admin.models.template_content_version import SUB_TEMP_CLOSE
from template_admin.models.template_content_version import SUB_TEMP_OPEN
from template_admin.models.template_content_version import TemplateContentVersion
from template_admin.models.template_version import TemplateVersion


def get_tvc_deps(tvc: TemplateContentVersion) -> list[dict]:
    deps = []
    content = tvc.content
    processed = []

    start = 0
    while True:
        idx = content.find(SUB_TEMP_OPEN, start)
        if idx == -1:
            break
        end = content.find(SUB_TEMP_CLOSE, idx + len(SUB_TEMP_OPEN))
        if end == -1:
            break

        start = end + len(SUB_TEMP_CLOSE)
        subtemp = content[idx + len(SUB_TEMP_OPEN) : end]
        if subtemp in processed:
            continue
        processed.append(subtemp)

        pattern = r"\s*(?P<module>[\w-]+) (?P<template>[\w-]+) \((?P<language>[\w-]+)\) \[(?P<version>\d+)\]\s*"
        match = re.search(pattern, subtemp)
        if match is None:
            continue

        module = match.group("module")
        template = match.group("template")
        language = match.group("language")
        version = int(match.group("version"))

        template = TemplateVersion.objects.filter(
            module=module,
            template=template,
            language=language,
        ).last()
        if template is None:
            continue

        version = template.version(version)
        if version is None:
            continue

        dep = {
            "module": template.module,
            "template": template.template,
            "language": template.language,
            "tmp_type": template.tmp_type,
            "custom": template.custom,
            "versions": [export_template_version_content(version)],
        }
        deps.append(dep)

    return deps


def export_template_version_content(tvc: TemplateContentVersion) -> dict:
    data = {
        "version": tvc.version,
        "created_date": tvc.created_date.strftime("%m/%d/%Y"),
        "content": tvc.content,
        "options": tvc.get_mapped_options(),
        "dependencies": get_tvc_deps(tvc),
    }
    return data


def export_template_version(temp: TemplateVersion) -> dict:
    data = {
        "module": temp.module,
        "template": temp.template,
        "language": temp.language,
        "tmp_type": temp.tmp_type,
        "custom": temp.custom,
        "versions": [
            export_template_version_content(tvc) for tvc in temp.versions.all()
        ],
    }

    return data
