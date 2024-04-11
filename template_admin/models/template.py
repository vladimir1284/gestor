from django.db import models


class Template(models.Model):
    module = models.CharField(max_length=100)
    template = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    content = models.TextField()

    def render(self, ctx) -> str:
        temp = Template(str(self.content))
        return temp.render(ctx)

    def get_content(self, **vars) -> str:
        content = str(self.content)
        for v in self.vars.all():
            content = v.replace(content, vars)

        return content

    def get_styled_content(self, **vars) -> str:
        content = self.get_content(**vars)
        return f'<link rel="stylesheet" href="/static/libs/ckeditor/ckeditor.css" /><div class="ck-content">{content}</div>'
