from template_admin.models.template import Template
from template_admin.tools.templates_tools import TT_LIST
import json

MODULE = "rent"
LANG_EN = "english"

CONTACT_REL = "emergency-contact-relations"

CONTACT_REL_DEF = """[
"Family",
"Friend",
"Other"
]"""

def init_temp_emergency_contact_relation():
    temp, c = Template.objects.get_or_create(
        module=MODULE,
        template=CONTACT_REL,
        language=LANG_EN,
        tmp_type=TT_LIST,
    )
    if c:
        temp.content = CONTACT_REL_DEF
        temp.save()

def get_emergency_contact_relations()-> list[str]:
    template = Template.objects.filter(
        module=MODULE,
        template=CONTACT_REL,
        language=LANG_EN,
    ).last()
    if template is None:
        return []

    try:
        print(template.content)
        data = json.loads(str(template.content))
    except Exception as e:
        print(e)
        return []

    return data

def get_emergency_contact_relations_choices() -> list[(str, str)]:
    data = get_emergency_contact_relations()
    reazons = [(None, "-----")] + [(r, r) for r in data]
    return reazons

