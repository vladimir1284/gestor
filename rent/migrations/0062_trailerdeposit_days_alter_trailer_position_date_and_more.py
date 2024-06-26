# Generated by Django 4.2.2 on 2024-05-07 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0061_set_trailers_pos'),
    ]

    operations = [
        migrations.AddField(
            model_name='trailerdeposit',
            name='days',
            field=models.IntegerField(default=7),
        ),
        migrations.AlterField(
            model_name='trailer',
            name='position_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trailer',
            name='position_note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
