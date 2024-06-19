from template_admin.models.template import Template
from template_admin.tools.templates_tools import TT_TEXT


class DefTemplate:
    def __init__(
        self,
        *,
        module: str,
        template: str,
        lang: str,
        content: str,
        ttype: str = TT_TEXT,
    ):
        self.module = module
        self.template = template
        self.lang = lang
        self.content = content
        self.ttype = ttype

    @property
    def tag(self):
        return f"[{self.module}].[{self.template}].[{self.lang}].[{self.ttype}]"

    def save(self):
        Template.objects.create(
            module=self.module,
            template=self.template,
            language=self.lang,
            tmp_type=self.ttype,
            content=self.content,
        )
