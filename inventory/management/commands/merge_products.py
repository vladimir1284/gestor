from inventory.models import Product, ProductTransaction, Stock, PriceReference, KitElement
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError


def merge_products(remaining_id, delete_id):
    try:
        remaining_product = Product.objects.get(id=remaining_id)
        delete_product = Product.objects.get(id=delete_id)

        # Update foreign key references
        update_foreign_keys(remaining_product, delete_product)

        # Delete the second instance
        delete_product.delete()

        print("Product merge successful!")

    except ObjectDoesNotExist:
        print("One or both product IDs are invalid.")


def update_foreign_keys(remaining_product, delete_product):
    # Update foreign key references in ProductTransaction
    ProductTransaction.objects.filter(
        product=delete_product).update(product=remaining_product)

    # Update foreign key references in Stock
    Stock.objects.filter(product=delete_product).update(
        product=remaining_product)

    # Update foreign key references in PriceReference
    PriceReference.objects.filter(
        product=delete_product).update(product=remaining_product)

    # Update foreign key references in KitElement
    KitElement.objects.filter(product=delete_product).update(
        product=remaining_product)


class Command(BaseCommand):
    help = 'Merge two Product instances into one.'

    def add_arguments(self, parser):
        parser.add_argument('remaining_id', type=int,
                            help="ID of the remaining instance")
        parser.add_argument("delete_id", type=int,
                            help="ID of the instance to be deleted")

    def handle(self, *args, **options):
        merge_products(options['remaining_id'], options['delete_id'])
