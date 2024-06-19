from template_admin.tools.init_def_template import DefTemplate
from template_admin.tools.init_def_version_template import DefVersionTemplate
from template_admin.tools.init_def_version_template import DefVersionTemplateContent
from template_admin.tools.template_initializer import add_template
from template_admin.tools.template_initializer import add_version_template
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
    # English
    # LTO
    with open(DEF_LTO_EN, "r") as templ:
        content = templ.read()
        add_version_template(
            DefVersionTemplate(
                module=MODULE,
                template=TEMPLATE_LTO,
                lang=LANG_EN,
                ttype=TT_TEXT,
                versions=[DefVersionTemplateContent(content=content)],
            )
        )
    # RENT
    with open(DEF_RENT_EN, "r") as templ:
        content = templ.read()
        add_version_template(
            DefVersionTemplate(
                module=MODULE,
                template=TEMPLATE_RENT,
                lang=LANG_EN,
                ttype=TT_TEXT,
                versions=[DefVersionTemplateContent(content=content)],
            )
        )

    # On hold
    # reasons
    add_template(
        DefTemplate(
            module=MODULE,
            template=TEMPLATE_ON_HOLD_REASONS,
            lang=LANG_EN,
            ttype=TT_LIST,
            content=ON_HOLD_REASONS,
        )
    )

    # ON HOLD EN
    with open(DEF_ONHOLD_EN, "r") as templ:
        content = templ.read()
        add_version_template(
            DefVersionTemplate(
                module=MODULE,
                template=TEMPLATE_ON_HOLD_CONDITIONS,
                lang=LANG_EN,
                ttype=TT_TEXT,
                versions=[DefVersionTemplateContent(content=content)],
            )
        )
    # ON HOLD ES
    with open(DEF_ONHOLD_ES, "r") as templ:
        content = templ.read()
        add_version_template(
            DefVersionTemplate(
                module=MODULE,
                template=TEMPLATE_ON_HOLD_CONDITIONS,
                lang=LANG_ES,
                ttype=TT_TEXT,
                versions=[DefVersionTemplateContent(content=content)],
            )
        )
