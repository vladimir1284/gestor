from django.contrib import admin

from template_admin.models.template import Template
from template_admin.models.template_content_version import \
    TemplateContentVersion
from template_admin.models.template_version import TemplateVersion
from template_admin.models.template_version_configs import \
    TemplateVersionConfig

# Register your models here.

admin.site.register(Template)
admin.site.register(TemplateVersion)
admin.site.register(TemplateVersionConfig)
admin.site.register(TemplateContentVersion)
