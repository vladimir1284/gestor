from rent.tools.init_conditions import LANG_EN
from rent.tools.init_conditions import MODULE
from rent.tools.init_conditions import TEMPLATE
from template_admin.models.template import Template


def get_conditions(ctx):
    language = LANG_EN

    template = Template.objects.filter(
        module=MODULE,
        template=TEMPLATE,
        language=language,
    ).last()
    if template is None:
        return None

    return template.render_template(ctx)

    # client: Associated = contract.lessee
    # trailer: Trailer = contract.trailer
    # mf: Manufacturer = None if trailer is None else trailer.manufacturer
    # user: User = contract.user

    # return template.get_styled_content(
    #     total_amount=contract.total_amount,
    #     contract_type=contract.contract_type,
    #     security_deposit=contract.security_deposit,
    #     contract_term=contract.contract_term,
    #     delayed_payments=contract.security_deposit,
    #     payment_frequency=contract.payment_frequency,
    #     stage=contract.stage,
    #     trailer_location=contract.trailer_location,
    #     effective_date=contract.effective_date,
    #     ended_date=contract.ended_date,
    #     final_debt=contract.final_debt,
    #     payment_amount=contract.payment_amount,
    #     service_charge=contract.service_charge,
    #     created_at=contract.created_at,
    #     updated_at=contract.updated_at,
    #     client_name=None if client is None else client.name,
    #     client_alias=None if client is None else client.alias,
    #     client_email=None if client is None else client.email,
    #     client_phone=None if client is None else client.phone_number,
    #     trailer_type=None if trailer is None else trailer.type,
    #     trailer_axis_number=None if trailer is None else trailer.axis_number,
    #     trailer_load=None if trailer is None else trailer.load,
    #     trailer_year=None if trailer is None else trailer.year,
    #     trailer_vin=None if trailer is None else trailer.vin,
    #     trailer_plate=None if trailer is None else trailer.plate,
    #     trailer_note=None if trailer is None else trailer.note,
    #     trailer_manufacturer_brand_name=None if mf is None else mf.brand_name,
    #     user_first_name=user.first_name,
    #     user_last_name=user.last_name,
    #     user_username=user.username,
    #     user_emial=user.email,
    # )
