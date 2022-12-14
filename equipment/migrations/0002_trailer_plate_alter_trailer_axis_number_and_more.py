# Generated by Django 4.1.2 on 2022-12-29 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trailer',
            name='plate',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='trailer',
            name='axis_number',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3)], verbose_name='Number of axles'),
        ),
        migrations.AlterField(
            model_name='trailer',
            name='load',
            field=models.IntegerField(choices=[(7, 7000), (8, 8000), (10, 10000), (12, 12000)], verbose_name='Axle load capacity'),
        ),
    ]
