from services.models.preorder import Preorder
from services.tools.init_conditions import LANG_EN
from services.tools.init_conditions import LANG_ES
from services.tools.init_conditions import MODULE
from services.tools.init_conditions import TEMPLATE
from template_admin.models.template import Template


def get_order_conditions(preorder: Preorder):
    language = LANG_ES
    if (
        preorder.preorder_data is not None
        and preorder.preorder_data.associated is not None
        and preorder.preorder_data.associated.language == LANG_EN
    ):
        language = LANG_EN

    template = Template.objects.filter(
        module=MODULE,
        template=TEMPLATE,
        language=language,
    ).last()
    if template is None:
        return None

    return template.get_styled_content(
        client_name=(
            None
            if preorder.preorder_data is None
            or preorder.preorder_data.associated is None
            else preorder.preorder_data.associated.name
        ),
        client_phone=(
            None
            if preorder.preorder_data is None
            or preorder.preorder_data.associated is None
            else preorder.preorder_data.associated.phone_number
        ),
        client_email=(
            None
            if preorder.preorder_data is None
            or preorder.preorder_data.associated is None
            else preorder.preorder_data.associated.email
        ),
    )
