# Generated by Django 4.1.2 on 2023-01-09 17:57

from django.db import migrations, models
import gdstorage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_alter_service_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='image',
            field=models.ImageField(blank=True, storage=gdstorage.storage.GoogleDriveStorage(), upload_to='images/expenses'),
        ),
        migrations.AlterField(
            model_name='service',
            name='sell_tax',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
