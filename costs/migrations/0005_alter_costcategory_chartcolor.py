# Generated by Django 4.1.5 on 2023-04-10 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0004_costcategory_chartcolor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costcategory',
            name='chartColor',
            field=models.CharField(choices=[('#696cff', 'violet'), ('#8592a3', 'gray'), ('#71dd37', 'green'), ('#ff3e1d', 'red'), ('#ffab00', 'yellow'), ('#03c3ec', 'blue'), ('#233446', 'black')], default='#8592a3', max_length=7),
        ),
    ]
