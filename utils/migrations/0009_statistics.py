# Generated by Django 4.1.2 on 2023-04-19 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0008_order_equipment_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_orders', models.IntegerField(default=0)),
                ('gross_income', models.FloatField(default=0)),
                ('profit_before_costs', models.FloatField(default=0)),
                ('labor_income', models.FloatField(default=0)),
                ('discount', models.FloatField(default=0)),
                ('third_party', models.FloatField(default=0)),
                ('supplies', models.FloatField(default=0)),
                ('costs', models.FloatField(default=0)),
                ('parts_cost', models.FloatField(default=0)),
                ('parts_price', models.FloatField(default=0)),
                ('payment_amount', models.FloatField(default=0)),
                ('transactions', models.IntegerField(default=0)),
                ('debt_created', models.FloatField(default=0)),
                ('debt_paid', models.FloatField(default=0)),
                ('debt_accumulated', models.FloatField(default=0)),
                ('membership_orders', models.IntegerField(default=0)),
                ('membership_amount', models.FloatField(default=0)),
                ('date', models.DateField()),
            ],
        ),
    ]
