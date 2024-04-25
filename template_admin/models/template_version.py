from django.apps import apps
from django.db import models
from django.template import Context
from django.template import Template as DT

from template_admin.tools.templates_tools import Style
from template_admin.tools.templates_tools import TT_TEXT


class TemplateVersion(models.Model):
    module = models.CharField(max_length=100)
    template = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    tmp_type = models.CharField(max_length=20, default=TT_TEXT)

    @property
    def last_version(self):
        last = self.version()
        if last is None:
            return 0
        return last.version

    def new_version(self, content: str = ""):
        TCV = apps.get_model("template_admin", "TemplateContentVersion")
        new_version = TCV(
            template=self,
            version=self.last_version + 1,
            content=content,
        )
        new_version.save()
        return new_version

    def version(self, version: int | None = None):
        if version is None:
            return self.versions.order_by("-version").first()
        return self.versions.filter(version=version).first()

    def render_template(self, ctx, version: int | None = None) -> str:
        version = self.version(version)
        if version is None:
            return ""
        content = f'{Style}<div class="ck-content">{str(version.content)}</div>'
        temp = DT(content)
        return temp.render(Context(ctx))
