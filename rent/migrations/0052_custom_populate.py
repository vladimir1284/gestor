from django.db import migrations, models


        


def populate_table(apps, schema_editor):
    SecurityDepositDevolution = apps.get_model('rent', 'securitydepositdevolution')
    db_alias = schema_editor.connection.alias
    for deposit in SecurityDepositDevolution.objects.using(db_alias).all():

        total_amount = sum([lease_deposit.amount for lease in deposit.contract.lease_set.all() for lease_deposit in lease.lease_deposit.all()])
        deposit.total_deposited_amount = total_amount
        deposit.save()
    


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0051_securitydepositdevolution_total_deposited_amount'),
    ]

    operations = [
        migrations.RunPython(populate_table)
    ]