# Generated by Django 4.2.2 on 2024-05-25 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0083_securitydepositdevolution_immediate_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='guarantor',
            name='guarantor_avatar',
            field=models.ImageField(blank=True, upload_to='images/guarantor_avatars/'),
        ),
    ]
