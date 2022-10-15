# Generated by Django 4.1.2 on 2022-10-14 01:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, upload_to='images/avatars')),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'Admin'), (2, 'Mecánico')], default=1)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
