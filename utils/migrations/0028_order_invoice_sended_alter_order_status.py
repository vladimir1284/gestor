# Generated by Django 4.2.2 on 2024-01-30 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0027_order_external'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice_sended',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('decline', 'Decline'), ('approved', 'Approved'), ('processing', 'Processing'), ('payment_pending', 'Payment pending'), ('complete', 'Complete')], default='pending', max_length=20),
        ),
    ]
