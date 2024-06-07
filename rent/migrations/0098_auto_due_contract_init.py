# Generated by Django 4.2.2 on 2024-06-07 01:40
from django.db import migrations


def init_due_contract(apps, schema):
    Due = apps.get_model("rent", "Due")
    dues = Due.objects.all()
    for due in dues:
        if due.lease is not None and due.lease.contract is not None:
            due.contract = due.lease.contract
            due.save()


class Migration(migrations.Migration):

    dependencies = [
        ("rent", "0097_due_contract"),
    ]

    operations = [migrations.RunPython(init_due_contract)]
