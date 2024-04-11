from template_admin.models.template import Template
from template_admin.models.template_vars import TemplateVars


DEF_COND = """
<ol>
    <li>Para iniciar la inspección, hay un cargo de $100, que no incluye la solución al problema.</li>
    <li>
        Por favor, ten en cuenta que no nos hacemos responsables de posibles pérdidas de herramientas o pertenencias en tu trailer durante su estancia aquí.
    </li>
    <li>Ofrecemos garantía por la mano de obra durante 30 días, pero no por las partes.</li>
    <li>
        Si decides no realizar el trabajo de inmediato, el almacenamiento tiene un costo de $10 al día. Este pago se realiza mensualmente por adelantado.
    </li>
    <li>
        El vehículo permanecerá en nuestras instalaciones hasta que se haya pagado el 100% del costo total del trabajo y almacenamiento.
    </li>
    <li>
        Durante las primeras 72 horas después de completar el trabajo, no hay cargos de almacenamiento. Después de este periodo, se aplican tarifas diarias.
    </li>
    <li>
        Nos esforzamos por ser eficientes en nuestro trabajo, pero si hay urgencia, háganoslo saber para coordinar de la mejor manera posible.
    </li>
    <li>
        Nuestro horario de servicio es de 8:30 am a 6:00 pm. Después de este horario, no realizamos trabajos bajo ninguna excepción.
    </li>
    <li>
        Todas las reglas son obligatorias. Si no estás de acuerdo con alguna, lamentablemente, no podremos llevar a cabo el servicio.
    </li>
</ol>
"""

MODULE = "services"
TEMPLATE = "order-conditions"
LANG = "spanish"

VARS = [
    {
        "pattern": "{{client_name}}",
        "var_name": "client_name",
    },
    {
        "pattern": "{{client_phone}}",
        "var_name": "client_phone",
    },
    {
        "pattern": "{{client_email}}",
        "var_name": "client_email",
    },
]


def set_vars(temp):
    ids = []
    for v in VARS:
        tv = temp.vars.filter(
            pattern=v["pattern"], var_name=v["var_name"]).first()
        if tv is None:
            tv = TemplateVars.objects.create(
                template=temp,
                pattern=v["pattern"],
                var_name=v["var_name"],
            )
        ids.append(tv.id)
    temp.vars.exclude(id__in=ids).delete()


def init_conditions():
    temp = Template.objects.filter(
        module=MODULE,
        template=TEMPLATE,
        language=LANG,
    ).last()
    if temp is None:
        temp = Template.objects.create(
            module=MODULE,
            template=TEMPLATE,
            language=LANG,
            content=DEF_COND,
        )
    set_vars(temp)
