# Generated by Django 4.1.5 on 2023-03-31 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_associated_membership_company_membership'),
    ]

    operations = [
        migrations.AddField(
            model_name='associated',
            name='debt',
            field=models.FloatField(default=0),
        ),
    ]
