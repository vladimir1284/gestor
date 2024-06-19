from template_admin.models.template import Template
from template_admin.models.template_version import TemplateVersion
from template_admin.tools.init_def_template import DefTemplate
from template_admin.tools.init_def_version_template import DefVersionTemplate


class TemplatesInitializer:
    _instance = None

    version_templates: list[DefVersionTemplate] = []
    templates: list[DefTemplate] = []

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TemplatesInitializer, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    def add_version_template(self, temp: DefVersionTemplate):
        self.version_templates.append(temp)

    def add_template(self, temp: DefTemplate):
        self.templates.append(temp)

    def init_version_templates(self):
        templates = TemplateVersion.objects.exclude(custom=True)
        temp_map = {}
        for t in templates:
            temp_map[t.tag] = t

        for dt in self.version_templates:
            if dt.tag not in temp_map:
                dt.save()

    def init_templates(self):
        templates = Template.objects.all()
        temp_map = {}
        for t in templates:
            temp_map[t.tag] = t

        for dt in self.templates:
            if dt.tag not in temp_map:
                dt.save()

    def init_all(self):
        self.init_version_templates()
        self.init_templates()


def add_template(temp: DefTemplate):
    TemplatesInitializer().add_template(temp)


def add_version_template(temp: DefVersionTemplate):
    TemplatesInitializer().add_version_template(temp)
