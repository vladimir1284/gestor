# Generated by Django 4.2.2 on 2023-10-12 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0033_leasedeposit_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='trailer',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='trailer',
            name='lease_to_own',
            field=models.BooleanField(default=False),
        ),
    ]
