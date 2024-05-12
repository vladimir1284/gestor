import re

from django.apps import apps
from django.db import models
from django.template import Context
from django.template import Template as DT

from template_admin.models.template_version_configs import \
    TemplateVersionConfig
from template_admin.tools.templates_tools import Style

SUB_TEMP_OPEN = "@{"
SUB_TEMP_CLOSE = "}@"


class TemplateContentVersion(models.Model):
    template = models.ForeignKey(
        "TemplateVersion",
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)
    content = models.TextField()

    def get_options(self) -> list[TemplateVersionConfig]:
        return self.options.all()

    def get_option_object(self, opt: str) -> TemplateVersionConfig | None:
        option = self.options.filter(option=opt).last()
        if option is None:
            return None
        return option

    def get_option(self, opt: str) -> str | None:
        option = self.get_option_object(opt)
        if option is None:
            return None
        return option.value

    def get_mapped_options(self) -> dict[str, str]:
        options = self.get_options()
        map = {}
        for o in options:
            map[o.option] = o.value
        return map

    def set_mapped_options(self, map: dict[str, str]):
        self.options.exclude(option__in=map.keys()).delete()

        for k, v in map.items():
            option = self.get_option_object(k)
            if option is not None:
                option.value = v
                option.save()
            else:
                TemplateVersionConfig.objects.create(
                    template=self,
                    option=k,
                    value=v,
                )

    def render_template(
        self,
        ctx,
        replaces: dict | None = None,
    ) -> str:
        content = f'{Style}<div class="ck-content">{str(self.content)}</div>'
        content = self.render_subtemplate(content, ctx, replaces)

        if replaces is not None:
            for k, v in replaces.items():
                content = content.replace(k, v)
        temp = DT(content)
        return temp.render(Context(ctx))

    def render_subtemplate(
        self,
        content,
        ctx,
        replaces: dict | None = None,
    ) -> str:
        # Get model TemplateVersion
        # Can not be imported becouse circular imports
        TemplateVersion = apps.get_model("template_admin", "TemplateVersion")
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

            subcontent = template.render_template(ctx, version, replaces)
            if subcontent is None:
                continue

            content = content.replace(
                SUB_TEMP_OPEN + subtemp + SUB_TEMP_CLOSE, subcontent
            )
            start = idx + len(subcontent)

        return content
