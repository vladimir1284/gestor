import json

from template_admin.models.template import Template
from template_admin.tools.templates_tools import TT_LIST

MODULE = "gestor"
LANG_EN = "english"

EMAIL_DOMAINS_TEMP = "email-domains"

EMAIL_DOMAINS_DEFAULT = """[
"@gmail.com",
"@yahoo.es",
"@ejemplo.com"
]"""


def init_temp_emails_domains():
    temp, c = Template.objects.get_or_create(
        module=MODULE,
        template=EMAIL_DOMAINS_TEMP,
        language=LANG_EN,
        tmp_type=TT_LIST,
    )
    if c:
        temp.content = EMAIL_DOMAINS_DEFAULT
        temp.save()


def get_email_domains() -> list[str]:
    template = Template.objects.filter(
        module=MODULE,
        template=EMAIL_DOMAINS_TEMP,
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

    return data


def get_email_domains_choices() -> list[(str, str)]:
    data = get_email_domains()
    return [(None, "-----")] + [(r, r) for r in data]
