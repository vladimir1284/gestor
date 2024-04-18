from services.models.preorder import Preorder
from services.tools.init_temps import LANG_EN
from services.tools.init_temps import LANG_ES
from services.tools.init_temps import MODULE
from services.tools.init_temps import TEMPLATE
from template_admin.models.template import Template


def get_order_conditions(preorder: Preorder, ctx):
    language = LANG_ES
    if preorder.associated is not None and preorder.associated.language == LANG_EN:
        language = LANG_EN

    template = Template.objects.filter(
        module=MODULE,
        template=TEMPLATE,
        language=language,
    ).last()
    if template is None:
        return None

    return template.render_template(ctx)
