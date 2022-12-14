# Generated by Django 4.1.2 on 2023-01-09 18:03

from django.db import migrations, models
import gdstorage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_service_image_alter_service_sell_tax'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='image',
        ),
        migrations.AddField(
            model_name='expense',
            name='image',
            field=models.ImageField(blank=True, storage=gdstorage.storage.GoogleDriveStorage(), upload_to='images/expenses'),
        ),
    ]
