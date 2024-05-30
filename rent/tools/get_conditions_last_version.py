from rent.tools.init_conditions import LANG_EN
from rent.tools.init_conditions import MODULE
from template_admin.models.template_version import TemplateVersion


def get_conditions_last_version(type="rent"):
    template = TemplateVersion.objects.filter(
        module=MODULE,
        template=type,
        language=LANG_EN,
    ).last()
    if template is None:
        return None
    return template.last_version
