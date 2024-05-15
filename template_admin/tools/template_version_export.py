import re

from template_admin.models.template_content_version import SUB_TEMP_CLOSE
from template_admin.models.template_content_version import SUB_TEMP_OPEN
from template_admin.models.template_content_version import TemplateContentVersion
from template_admin.models.template_version import TemplateVersion


def get_tvc_deps(tvc: TemplateContentVersion) -> list[dict]:
    deps = []
    content = tvc.content
    processed = []

    dependencies = {}

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

        if subtemp in dependencies:
            dependencies[subtemp]["versions"].append(version)
        else:
            dependencies[subtemp] = {
                "module": module,
                "template": template,
                "language": language,
                "versions": [version],
            }

    for v in dependencies.values():
        template = TemplateVersion.objects.filter(
            module=v["module"],
            template=v["template"],
            language=v["language"],
        ).last()
        if template is None:
            continue
        deps.append(export_template_version(template, v["versions"]))

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


def export_template_version(
    temp: TemplateVersion,
    versions: list[int] | None = None,
) -> dict:
    if versions is None:
        versions = [export_template_version_content(tvc) for tvc in temp.versions.all()]
    else:
        versions = [
            export_template_version_content(tvc)
            for tvc in temp.versions.filter(version__in=versions)
        ]
    data = {
        "module": temp.module,
        "template": temp.template,
        "language": temp.language,
        "tmp_type": temp.tmp_type,
        "custom": temp.custom,
        "versions": versions,
    }

    return data
