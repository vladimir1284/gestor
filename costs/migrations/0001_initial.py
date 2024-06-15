# Generated by Django 4.2.2 on 2024-06-12 18:49
import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CostCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120, unique=True)),
                (
                    "chartColor",
                    models.CharField(
                        choices=[
                            ("#696cff", "violet"),
                            ("#8592a3", "gray"),
                            ("#71dd37", "green"),
                            ("#ff3e1d", "red"),
                            ("#ffab00", "yellow"),
                            ("#03c3ec", "blue"),
                            ("#233446", "black"),
                        ],
                        default="#8592a3",
                        max_length=7,
                    ),
                ),
                ("icon", models.ImageField(blank=True, upload_to="images/icons")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Cost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("concept", models.CharField(max_length=120)),
                ("image", models.ImageField(blank=True, upload_to="images/costs")),
                ("note", models.TextField(blank=True)),
                ("created_date", models.DateField(auto_now_add=True)),
                ("date", models.DateField()),
                ("amount", models.FloatField()),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="costs.costcategory",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "related_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="related_to",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Associated",
                    ),
                ),
            ],
        ),
    ]
