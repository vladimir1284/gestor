from django.db import models

from template_admin.models.template import Template


TV_STR = "STR"
TV_DATE = "DATE"
TV_INT = "INT"
TV_FLOAT = "FLOAT"

TV_TYPES = [
    (TV_STR, TV_STR),
    (TV_DATE, TV_DATE),
    (TV_INT, TV_INT),
    (TV_FLOAT, TV_FLOAT),
]


class TemplateVars(models.Model):
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="vars",
    )
    pattern = models.CharField(max_length=100)
    var_name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=TV_TYPES, null=True)

    def getVar(self, vars: dict) -> str:
        if self.var_name not in vars:
            return f"UNKNOWN[{self.var_name} not found]"
        if vars[self.var_name] is None:
            return "___"
        v = vars[self.var_name]

        try:
            if self.type == TV_FLOAT:
                return f"{v:.2}"
            if self.type == TV_DATE:
                return v.strftime("%B %d, %Y")
        except Exception as e:
            print(e)

        return str(v)

    def replace(self, content: str, vars: dict) -> str:
        return content.replace(
            str(self.pattern),
            self.getVar(vars),
        )


class TV:
    def __init__(self, name: str, pattern: str = "", type: str = ""):
        self.pattern = "{{" + name + "}}" if pattern == "" else pattern
        self.name = name
        self.type = type


def set_vars(temp, vars: list[TV]):
    ids = []
    for v in vars:
        tv = temp.vars.filter(pattern=v.pattern, var_name=v.name).first()
        if tv is None:
            tv = TemplateVars.objects.create(
                template=temp,
                pattern=v.pattern,
                var_name=v.name,
            )
        ids.append(tv.id)
    temp.vars.exclude(id__in=ids).delete()
