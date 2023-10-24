# Generated by Django 4.2.2 on 2023-10-23 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0039_due_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='contract_type',
            field=models.CharField(choices=[('lto', 'Lease to own'), ('rent', 'Rent')], default='rent', max_length=10),
        ),
        migrations.AddField(
            model_name='contract',
            name='total_amount',
            field=models.IntegerField(default=0),
        ),
    ]
