# Generated by Django 4.2.2 on 2024-05-04 12:15
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("rent", "0063_set_old_contract_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="contract",
            name="client_complete",
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
