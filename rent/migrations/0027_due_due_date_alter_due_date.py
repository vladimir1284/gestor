from django.db import migrations, models


def delete_all_due_instances(apps, schema_editor):
    Due = apps.get_model('rent', 'Due')
    Due.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0026_alter_payment_amount'),
    ]

    operations = [
        migrations.RunSQL(
            sql='DELETE FROM rent_due;',
            reverse_sql='INSERT INTO rent_due (id, due_date, date) SELECT id, due_date, date FROM rent_due;',
        ),
        migrations.AddField(
            model_name='due',
            name='due_date',
            field=models.DateField(),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='due',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
