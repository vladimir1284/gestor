# Generated by Django 4.1.2 on 2022-11-10 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_associated_avatar_alter_productcategory_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='associated',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='images/avatars'),
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='icon',
            field=models.ImageField(blank=True, upload_to='images/icons'),
        ),
    ]
