# Generated by Django 4.2.2 on 2023-10-06 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0032_leasedeposit'),
    ]

    operations = [
        migrations.AddField(
            model_name='leasedeposit',
            name='note',
            field=models.TextField(blank=True),
        ),
    ]
