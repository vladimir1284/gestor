# Generated by Django 4.1.5 on 2023-06-12 23:24

from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


def create_debt_status(apps, schema_editor):
    Associated = apps.get_model('users', 'Associated')
    DebtStatus = apps.get_model('services', 'DebtStatus')
    debtors = Associated.objects.filter(~Q(debt=0))

    for client in debtors:
        if client.debt > 0:
            DebtStatus.objects.create(client=client)
        else:
            client.debt = 0
            client.save()


def reverse_debt_status(apps, schema_editor):
    DebtStatus = apps.get_model('services', 'DebtStatus')
    DebtStatus.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_associated_debt'),
        ('services', '0020_alter_paymentcategory_chartcolor_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DebtStatus',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), (
                    'cleared', 'Cleared'), ('lost', 'Lost')], default='pending', max_length=20)),
                ('client', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='users.associated')),
            ],
        ),
        migrations.RunPython(create_debt_status,
                             reverse_code=reverse_debt_status),
    ]
