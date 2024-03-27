# Generated by Django 4.2.2 on 2024-03-27 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0030_order_storage_reason_ordertrace_reason_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='storage_reason',
            field=models.CharField(blank=True, choices=[('capacity', 'Falta de capacidad en el taller'), ('approval', 'Pendiente por aprobación del cliente'), ('ready', 'Listo para recoger'), ('storage_service', 'Servicio de storage')], default='storage_service', max_length=20, null=True),
        ),
    ]
