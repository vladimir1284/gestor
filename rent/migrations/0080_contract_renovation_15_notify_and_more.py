# Generated by Django 4.2.2 on 2024-05-21 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0079_contractrenovation'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='renovation_15_notify',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contract',
            name='renovation_7_notify',
            field=models.BooleanField(default=False),
        ),
    ]
