# Generated by Django 4.2.2 on 2023-07-29 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0022_auto_20230616_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='internal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='service',
            name='marketing',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='service',
            name='tire',
            field=models.BooleanField(default=False),
        ),
    ]
