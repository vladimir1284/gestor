from rent.models.lease import Contract
from rent.tools.init_conditions import LANG_EN
from rent.tools.init_conditions import MODULE
from rent.tools.init_conditions import TEMPLATE_LTO
from rent.tools.init_conditions import TEMPLATE_RENT
from template_admin.models.template_version import TemplateVersion


def get_conditions(ctx):
    contract: Contract = ctx["contract"]
    templ = TEMPLATE_RENT if contract.contract_type == "rent" else TEMPLATE_LTO
    version = contract.template_version

    language = LANG_EN

    template = TemplateVersion.objects.filter(
        module=MODULE,
        template=templ,
        language=language,
    ).last()
    if template is None:
        return None

    return template.render_template(ctx, version=version)
