# Generated by Django 4.2.2 on 2024-04-08 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0028_autogenerate_preorder_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='preorderdata',
            name='ready',
            field=models.BooleanField(null=True),
        ),
    ]
