# Generated by Django 4.2.2 on 2023-08-22 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0013_lesseedata_client_id_lesseedata_contact_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='delayed_payments',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='contract',
            name='ended_date',
            field=models.DateField(null=True),
        ),
    ]
