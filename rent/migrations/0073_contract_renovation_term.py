# Generated by Django 4.2.2 on 2024-05-17 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0072_alter_contract_guarantor'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='renovation_term',
            field=models.IntegerField(default=3),
        ),
    ]
