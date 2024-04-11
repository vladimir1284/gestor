from services.models.preorder import Preorder
from template_admin.models.template import Template


def get_order_conditions(preorder: Preorder):
    template = Template.objects.filter().last()
    if template is None:
        return None

    return template.get_content(
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
