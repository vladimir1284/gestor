from template_admin.models.template_version import TemplateContentVersion
from template_admin.models.template_version import TemplateVersion
from template_admin.models.template_version import TemplateVersionConfig
from template_admin.tools.templates_tools import TT_TEXT


class DefVersionTemplateContent:
    def __init__(
        self,
        *,
        content: str,
        version: int | None = None,
        conf: dict[str, str] = {},
    ):
        self.content = content
        self.version = version
        self.conf = conf

    def save(self, temp: TemplateVersion):
        if self.version is None:
            self.version = temp.last_version + 1

        version_content = TemplateContentVersion.objects.create(
            template=temp,
            version=self.version,
            content=self.content,
        )

        for opt, val in self.conf.items():
            TemplateVersionConfig.objects.create(
                template=version_content,
                option=opt,
                value=val,
            )


class DefVersionTemplate:
    def __init__(
        self,
        *,
        module: str,
        template: str,
        lang: str,
        versions: list[DefVersionTemplateContent],
        ttype: str = TT_TEXT,
    ):
        self.module = module
        self.template = template
        self.lang = lang
        self.versions = versions
        self.ttype = ttype

    @property
    def tag(self):
        return f"[{self.module}].[{self.template}].[{self.lang}].[{self.ttype}]"

    def save_versions(self, temp: TemplateVersion):
        for ver in self.versions:
            ver.save(temp)

    def save(self):
        temp = TemplateVersion.objects.create(
            module=self.module,
            template=self.template,
            language=self.lang,
            tmp_type=self.ttype,
        )
        self.save_versions(temp)
