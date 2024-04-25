from django.db import models
from django.template import Context
from django.template import Template as DT

from template_admin.models.template_version import TemplateVersion
from template_admin.tools.templates_tools import Style


class TemplateContentVersion(models.Model):
    template = models.ForeignKey(
        TemplateVersion,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)
    content = models.TextField()

    def render_template(self, ctx) -> str:
        content = f'{Style}<div class="ck-content">{str(self.content)}</div>'
        temp = DT(content)
        return temp.render(Context(ctx))
