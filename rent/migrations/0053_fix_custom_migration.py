from django.db import migrations, models


        


def populate_table(apps, schema_editor):
    SecurityDepositDevolution = apps.get_model('rent', 'securitydepositdevolution')
    Contract = apps.get_model('rent', 'Contract')
    db_alias = schema_editor.connection.alias
    for contract in Contract.objects.using(db_alias).all():
        deposit, c = SecurityDepositDevolution.objects.using(db_alias).get_or_create(contract=contract)
        total_amount = sum([lease_deposit.amount for lease in contract.lease_set.all() for lease_deposit in lease.lease_deposit.all()])
        deposit.total_deposited_amount = total_amount
        deposit.save()
    


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0052_custom_populate'),
    ]

    operations = [
        migrations.RunPython(populate_table)
    ]