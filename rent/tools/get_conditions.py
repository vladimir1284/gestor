import json

from dateutil.relativedelta import relativedelta

from rent.models.lease import Contract
from rent.models.trailer_deposit import TrailerDeposit
from rent.tools.init_conditions import LANG_EN
from rent.tools.init_conditions import MODULE
from rent.tools.init_conditions import TEMPLATE_LTO
from rent.tools.init_conditions import TEMPLATE_ON_HOLD_CONDITIONS
from rent.tools.init_conditions import TEMPLATE_ON_HOLD_REASONS
from rent.tools.init_conditions import TEMPLATE_RENT
from template_admin.models.template import Template
from template_admin.models.template_version import TemplateVersion


def get_rent_conditions_template() -> TemplateVersion:
    return TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_RENT,
        language=LANG_EN,
    ).last()


def contract_guarantor(contract: Contract) -> bool:
    template, version = get_rent_conditions_template_from_contract(contract)
    return template is not None and template.option(version, "guarantor") == "true"


def get_rent_conditions_template_from_contract(contract: Contract):
    language = LANG_EN
    templ = TEMPLATE_RENT if contract.contract_type == "rent" else TEMPLATE_LTO
    version = contract.template_version

    template = TemplateVersion.objects.filter(
        module=MODULE,
        template=templ,
        language=language,
    ).last()
    if template is None:
        return None, 0

    return template, version


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

    template, version = get_rent_conditions_template_from_contract(contract)
    if template is None:
        return None

    replaces = {
        "@@signatures_and_date@@": '{% include "rent/contract/signatures_and_date.html" %}',
        "@@signatures_and_date_v2@@": '{% include "rent/contract/signatures_and_date_v2.html" %}',
        "@@trailer_report@@": '{% include "rent/contract/trailer_condition_report.html" %}',
        "@@lessee_signature@@": '<img class="signature" src="{{ signature_lessee.img.url }}">',
        # dates
        "@@date_daniel@@": '{% include "rent/contract/signatures/date_daniel.html" %}',
        "@@date_lessee@@": '{% include "rent/contract/signatures/date_lessee.html" %}',
        "@@date_guarantor@@": '{% include "rent/contract/signatures/date_guarantor.html" %}',
        # Sign
        "@@sign_lessee@@": '{% include "rent/contract/signatures/sign_lessee.html" %}',
        "@@sign_guarantor@@": '{% include "rent/contract/signatures/sign_guarantor.html" %}',
        "@@sign_daniel@@": '{% include "rent/contract/signatures/show_sign_daniel.html" %}',
        # SHOW
        # dates
        "@@show_date_daniel@@": '{% include "rent/contract/signatures/show_date_daniel.html" %}',
        "@@show_date_lessee@@": '{% include "rent/contract/signatures/show_date_lessee.html" %}',
        "@@show_date_guarantor@@": '{% include "rent/contract/signatures/show_date_guarantor.html" %}',
        # Sign
        "@@show_sign_lessee@@": '{% include "rent/contract/signatures/show_sign_lessee.html" %}',
        "@@show_sign_guarantor@@": '{% include "rent/contract/signatures/show_sign_guarantor.html" %}',
        "@@show_sign_daniel@@": '{% include "rent/contract/signatures/show_sign_daniel.html" %}',
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


def get_on_hold_reasons():
    template = Template.objects.filter(
        module=MODULE,
        template=TEMPLATE_ON_HOLD_REASONS,
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

    reazons = [(None, "-----")] + [(r, r) for r in data]
    return reazons


def get_on_hold_conditions_last_version() -> int:
    template = TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_ON_HOLD_CONDITIONS,
        language=LANG_EN,
    ).last()
    return template.last_version


def get_on_hold_conditions(ctx: dict) -> str:
    on_hold: TrailerDeposit = ctx["deposit"]
    template = TemplateVersion.objects.filter(
        module=MODULE,
        template=TEMPLATE_ON_HOLD_CONDITIONS,
        language=on_hold.client.language,
    ).last()
    if template is None:
        return ""

    return template.render_template(ctx, on_hold.template_version)
