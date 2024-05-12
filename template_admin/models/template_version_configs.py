from django.db import models

from template_admin.models.template_version import TemplateVersion


class TemplateVersionConfig(models.Model):
    template = models.ForeignKey(TemplateVersion, on_delete=models.CASCADE)
    option = models.CharField(max_length=100)
