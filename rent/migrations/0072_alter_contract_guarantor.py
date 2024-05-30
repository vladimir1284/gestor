# Generated by Django 4.2.2 on 2024-05-16 16:38
import django.db.models.deletion
from django.db import migrations
from django.db import models


def removeGuarantors(apps, scheme):
    Contract = apps.get_model("rent", "Contract")
    contracts = Contract.objects.exclude(guarantor=None)
    for c in contracts:
        c.guarantor = None
        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ("rent", "0071_guarantor"),
    ]

    operations = [
        migrations.RunPython(removeGuarantors),
        migrations.AlterField(
            model_name="contract",
            name="guarantor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="rent.guarantor",
            ),
        ),
    ]
