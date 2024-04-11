from django.db import models

from template_admin.models.template import Template


class TemplateVars(models.Model):
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="vars",
    )
    pattern = models.CharField(max_length=100)
    var_name = models.CharField(max_length=100)

    def getVar(self, vars: dict) -> str:
        if self.var_name not in vars:
            return f"UNKNOWN[{self.var_name} not found]"
        if vars[self.var_name] is None:
            return "___"
        return str(vars[self.var_name])

    def replace(self, content: str, vars: dict) -> str:
        return content.replace(
            str(self.pattern),
            self.getVar(vars),
        )
