from template_admin.models.template import Template
from template_admin.models.template_version import TemplateVersion
from template_admin.tools.templates_tools import TT_LIST
from template_admin.tools.templates_tools import TT_TEXT

MODULE = "rent"
LANG_EN = "english"
LANG_ES = "spanish"

UPDATE_ON_HOLD_REASONS = False

TEMPLATE_LTO = "lease-conditions-lto"
TEMPLATE_RENT = "lease-conditions-rent"
TEMPLATE_ON_HOLD_REASONS = "on-hold-reasons"
TEMPLATE_ON_HOLD_CONDITIONS = "on-hold-conditions"

DEF_LTO_EN = "rent/tools/conditions_default_templates/lto.html"
DEF_RENT_EN = "rent/tools/conditions_default_templates/rent.html"

DEF_ONHOLD_EN = "rent/tools/conditions_default_templates/on_hold_en.html"
DEF_ONHOLD_ES = "rent/tools/conditions_default_templates/on_hold_es.html"

ON_HOLD_REASONS = """[
"Reason 1",
"Reason 2",
"Reason 3"
]"""


def init_conditions():
    init_on_hold_reason()
    init_on_hold_conditions()
    # English
    # LTO
    temp = TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_LTO,
        language=LANG_EN,
        tmp_type=TT_TEXT,
    ).last()
    if temp is None:
        with open(DEF_LTO_EN, "r") as templ:
            content = templ.read()
            temp = TemplateVersion.objects.create(
                module=MODULE,
                template=TEMPLATE_LTO,
                language=LANG_EN,
                tmp_type=TT_TEXT,
            )
            temp.new_version(content=content)
    # RENT
    temp = TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_RENT,
        language=LANG_EN,
        tmp_type=TT_TEXT,
    ).last()
    if temp is None:
        with open(DEF_RENT_EN, "r") as templ:
            content = templ.read()
            temp = TemplateVersion.objects.create(
                module=MODULE,
                template=TEMPLATE_RENT,
                language=LANG_EN,
                tmp_type=TT_TEXT,
            )
            temp.new_version(content=content)


def init_on_hold_reason():
    temp, c = Template.objects.get_or_create(
        module=MODULE,
        template=TEMPLATE_ON_HOLD_REASONS,
        language=LANG_EN,
        tmp_type=TT_LIST,
    )
    if c or UPDATE_ON_HOLD_REASONS:
        temp.content = ON_HOLD_REASONS
        temp.save()


def init_on_hold_conditions():
    # ON HOLD EN
    temp = TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_ON_HOLD_CONDITIONS,
        language=LANG_EN,
        tmp_type=TT_TEXT,
    ).last()
    if temp is None:
        with open(DEF_ONHOLD_EN, "r") as templ:
            content = templ.read()
            temp = TemplateVersion.objects.create(
                module=MODULE,
                template=TEMPLATE_ON_HOLD_CONDITIONS,
                language=LANG_EN,
                tmp_type=TT_TEXT,
            )
            temp.new_version(content=content)
    # ON HOLD ES
    temp = TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_ON_HOLD_CONDITIONS,
        language=LANG_ES,
        tmp_type=TT_TEXT,
    ).last()
    if temp is None:
        with open(DEF_ONHOLD_ES, "r") as templ:
            content = templ.read()
            temp = TemplateVersion.objects.create(
                module=MODULE,
                template=TEMPLATE_ON_HOLD_CONDITIONS,
                language=LANG_ES,
                tmp_type=TT_TEXT,
            )
            temp.new_version(content=content)
