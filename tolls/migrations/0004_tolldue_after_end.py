# Generated by Django 4.2.2 on 2024-06-13 19:42
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("tolls", "0003_tolldue_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="tolldue",
            name="after_end",
            field=models.BooleanField(null=True),
        ),
    ]
