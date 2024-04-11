from django.db import models
from django.template import Context, Template as DT


Style = """
{%load static%}
<link rel="stylesheet" href="{%static 'libs/ckeditor/ckeditor.css'%}" />
"""


class Template(models.Model):
    module = models.CharField(max_length=100)
    template = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    content = models.TextField()

    def render_template(self, ctx) -> str:
        content = f'{Style}<div class="ck-content">{str(self.content)}</div>'
        temp = DT(content)
        return temp.render(Context(ctx))
