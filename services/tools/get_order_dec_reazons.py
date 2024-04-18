import json

from services.tools.init_temps import DEC_REAZONS
from services.tools.init_temps import LANG_ES
from services.tools.init_temps import MODULE
from template_admin.models.template import Template


def get_order_dec_reazons():
    template = Template.objects.filter(
        module=MODULE,
        template=DEC_REAZONS,
        language=LANG_ES,
    ).last()
    print(template)
    if template is None:
        return []

    try:
        data = json.loads(str(template.content))
    except Exception as e:
        print(e)
        return

    reazons = [(None, "-----")] + [(r, r) for r in data]
    print(reazons)
    return reazons
