# Generated by Django 4.1.2 on 2023-01-09 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_associated_language_alter_company_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='associated',
            name='outsource',
            field=models.BooleanField(default=False, verbose_name='Outsource'),
        ),
    ]
