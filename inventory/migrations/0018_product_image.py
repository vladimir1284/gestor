# Generated by Django 4.1.2 on 2022-12-09 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_rename_transaction_producttransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, upload_to='images/products'),
        ),
    ]
