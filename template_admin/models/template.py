from django.db import models
from django.template import Context
from django.template import Template as DT


Style = """
{%load static%}
<link rel="stylesheet" href="{%static 'libs/ckeditor/ckeditor.css'%}" />
"""

TT_TEXT = "text"
TT_LIST = "list"


class Template(models.Model):
    module = models.CharField(max_length=100)
    template = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    tmp_type = models.CharField(max_length=20, default=TT_TEXT)
    content = models.TextField()

    def render_template(self, ctx) -> str:
        content = f'{Style}<div class="ck-content">{str(self.content)}</div>'
        temp = DT(content)
        return temp.render(Context(ctx))
