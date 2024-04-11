from django.db import models


class Template(models.Model):
    module = models.CharField(max_length=100)
    template = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    content = models.TextField()

    def get_content(self, **vars) -> str:
        content = str(self.content)
        for v in self.vars.all():
            content = v.replace(content, vars)
        return content
