from template_admin.models.template import Template
from template_admin.models.template_vars import set_vars
from template_admin.models.template_vars import TV


DEF_COND_ES = """
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
DEF_COND_EN = """
<ol> <li>To start the inspection, there is a charge of $100, which does not include the solution to the problem.</li> <li>Please note that we are not responsible for possible losses of tools or belongings in your trailer during its stay here.</li> <li>We offer a warranty for labor for 30 days, but not for parts.</li> <li>If you decide not to do the work immediately, storage costs $10 a day. This payment is made monthly in advance.</li> <li>The vehicle will remain in our facilities until 100% of the total cost of work and storage has been paid.</li> <li>During the first 72 hours after completing the work, there are no storage charges. After this period, daily rates apply.</li> <li>We strive to be efficient in our work, but if there is urgency, let us know to coordinate in the best possible way.</li> <li>Our service hours are from 8:30 am to 6:00 pm. After this time, we do not perform work under any exception.</li> <li>All rules are mandatory. If you do not agree with any, unfortunately, we will not be able to carry out the service.</li> </ol>
"""

MODULE = "services"
TEMPLATE = "order-conditions"
LANG_ES = "spanish"
LANG_EN = "english"

VARS = [
    TV(
        name="client_name",
    ),
    TV(
        name="client_phone",
    ),
    TV(
        name="client_email",
    ),
]


def init_conditions():
    # Spanish
    temp = Template.objects.filter(
        module=MODULE,
        template=TEMPLATE,
        language=LANG_ES,
    ).last()
    if temp is None:
        temp = Template.objects.create(
            module=MODULE,
            template=TEMPLATE,
            language=LANG_ES,
            content=DEF_COND_ES,
        )
    set_vars(temp, VARS)

    # English
    temp = Template.objects.filter(
        module=MODULE,
        template=TEMPLATE,
        language=LANG_EN,
    ).last()
    if temp is None:
        temp = Template.objects.create(
            module=MODULE,
            template=TEMPLATE,
            language=LANG_EN,
            content=DEF_COND_EN,
        )
    set_vars(temp, VARS)
