# Generated by Django 4.2.2 on 2023-11-17 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0042_remove_payment_remaining'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='final_debt',
            field=models.FloatField(default=0),
        ),
    ]
