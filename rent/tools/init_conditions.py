from template_admin.models.template_version import TemplateVersion
from template_admin.tools.templates_tools import TT_TEXT

DEF_LTO_EN = "rent/tools/conditions_default_templates/lto.html"
DEF_RENT_EN = "rent/tools/conditions_default_templates/rent.html"

MODULE = "rent"
TEMPLATE_LTO = "lease-conditions-lto"
TEMPLATE_RENT = "lease-conditions-rent"
LANG_EN = "english"


def init_conditions():
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
