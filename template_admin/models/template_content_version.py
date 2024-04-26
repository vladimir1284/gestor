from django.db import models
from django.template import Context
from django.template import Template as DT

from template_admin.tools.templates_tools import Style


class TemplateContentVersion(models.Model):
    template = models.ForeignKey(
        "TemplateVersion",
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)
    content = models.TextField()

    def render_template(
        self,
        ctx,
        replaces: dict | None = None,
    ) -> str:
        content = f'{Style}<div class="ck-content">{str(self.content)}</div>'
        if replaces is not None:
            for k, v in replaces.items():
                content = content.replace(k, v)
        temp = DT(content)
        return temp.render(Context(ctx))
