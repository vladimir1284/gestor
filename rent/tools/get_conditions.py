from dateutil.relativedelta import relativedelta

from rent.models.lease import Contract
from rent.tools.init_conditions import LANG_EN
from rent.tools.init_conditions import MODULE
from rent.tools.init_conditions import TEMPLATE_LTO
from rent.tools.init_conditions import TEMPLATE_RENT
from template_admin.models.template_version import TemplateVersion


def get_rent_conditions_template() -> TemplateVersion:
    return TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_RENT,
        language=LANG_EN,
    ).last()


def get_conditions(ctx):
    contract: Contract = ctx["contract"]

    # Lessee Initials
    client_initials = ""
    client_name = contract.lessee.name
    for n in client_name.split(" "):
        if n != "":
            client_initials += n[0].upper()
    ctx["lessee_initials"] = client_initials

    delta = relativedelta(months=contract.contract_term)

    contract.end_date = contract.effective_date + delta

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

    replaces = {
        "@@signatures_and_date@@": '{% include "rent/contract/signatures_and_date.html" %}',
        "@@signatures_and_date_v2@@": '{% include "rent/contract/signatures_and_date_v2.html" %}',
        "@@trailer_report@@": '{% include "rent/contract/trailer_condition_report.html" %}',
        "@@lessee_signature@@": '<img class="signature" src="{{ signature_lessee.img.url }}">',
    }
    cond = template.render_template(
        ctx,
        version=version,
        replaces=replaces,
    )
    if cond is None:
        cond = template.render_template(
            ctx,
            replaces=replaces,
        )
    return cond
