# Generated by Django 4.2.2 on 2024-02-01 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0028_order_invoice_sended_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='external',
        ),
    ]
