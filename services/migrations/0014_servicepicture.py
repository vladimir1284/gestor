# Generated by Django 4.1.5 on 2023-03-17 10:40
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0008_order_equipment_type"),
        ("services", "0013_remove_service_max_price"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServicePicture",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="images/services")),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_picture",
                        to="utils.order",
                    ),
                ),
            ],
        ),
    ]
