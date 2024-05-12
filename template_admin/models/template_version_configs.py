from django.db import models


class TemplateVersionConfig(models.Model):
    template = models.ForeignKey(
        "TemplateContentVersion", on_delete=models.CASCADE, related_name="options"
    )
    option = models.CharField(max_length=100)
    value = models.TextField()
