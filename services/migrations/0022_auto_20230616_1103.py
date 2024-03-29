# Generated by Django 3.2.19 on 2023-06-16 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0021_debtstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='debtstatus',
            name='amount_due_per_week',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='debtstatus',
            name='last_modified_date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='debtstatus',
            name='weeks',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
