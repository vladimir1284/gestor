from django.test import TestCase
from django.urls import reverse

from inventory.forms import OrderCreateForm as P_OrderCreateForm
from inventory.forms import TransactionCreateForm
from inventory.models import Product
from inventory.models import ProductTransaction
from inventory.models import Stock
from inventory.models import Unit
from inventory.views.order import undo_transaction
from inventory.views.transaction import handle_transaction
from services.forms import OrderCreateForm as S_OrderCreateForm
from services.tools.transaction import handle_order_transactions
from services.tools.transaction import reverse_order_transactions
from users.models import Associated
from users.models import User
from utils.models import Order

Quantity = 100


class InventoryFullTestCase(TestCase):
    def create_provider(self):
        self.provider = Associated.objects.create(
            type="provider",
            active=True,
            name="TestProvider",
        )
        self.assertIsNotNone(self.provider)
        self.assertIsNotNone(self.provider.id)

    def create_client(self):
        self.associated = Associated.objects.create(
            type="client",
            active=True,
            name="TestClient",
        )
        self.assertIsNotNone(self.associated)
        self.assertIsNotNone(self.associated.id)

    def create_user(self):
        self.user = User.objects.create(
            username="Tester",
            password="1231231234",
            is_superuser=True,
            is_active=True,
            is_staff=True,
        )
        self.assertIsNotNone(self.user)
        self.assertIsNotNone(self.user.id)

    def create_unit(self):
        self.unit = Unit.objects.create(name="U", magnitude="U", factor=1)
        self.assertIsNotNone(self.unit)
        self.assertIsNotNone(self.unit.id)

    def create_product(self):
        self.product = Product.objects.create(
            name="TestProd",
            active=True,
            description="Just for testing",
            unit=self.unit,
            type="part",
        )
        self.assertIsNotNone(self.product)
        self.assertIsNotNone(self.product.id)

    def create_porder(self):
        data = {
            "concept": "initial_test",
            "note": "Testing",
            "associated": self.provider,
            "position": None,
        }

        form = P_OrderCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

        self.porder: Order = form.save(commit=False)
        self.porder.created_by = self.user
        self.porder.save()

        self.assertIsNotNone(self.porder)
        self.assertIsNotNone(self.porder.id)

    def create_porder_transaction(self):
        form = TransactionCreateForm(
            product=self.product,
            order=self.porder,
            data={
                "price": self.product.getSuggestedPrice(),
                "note": "Testing",
                "quantity": Quantity,
                "unit": self.product.unit,
                "tax": 8,
            },
        )
        self.assertTrue(form.is_valid(), form.errors)

        self.porder_transaction: ProductTransaction = form.save(commit=False)
        self.porder_transaction.order = self.porder
        self.porder_transaction.product = self.product
        self.porder_transaction.save()

        self.assertIsNotNone(self.porder_transaction)
        self.assertIsNotNone(self.porder_transaction.id)

    def complete_porder(self):
        transactions = ProductTransaction.objects.filter(order=self.porder)
        for transaction in transactions:
            handle_transaction(transaction)
        self.porder.status = "complete"
        self.porder.save()

        self.porder = Order.objects.get(id=self.porder.id)
        self.assertEqual(self.porder.status, "complete")

    def decline_porder(self):
        transactions = ProductTransaction.objects.filter(order=self.porder)
        for transaction in transactions:
            undo_transaction(transaction)
        self.porder.status = "complete"
        self.porder.save()

        self.porder = Order.objects.get(id=self.porder.id)
        self.assertEqual(self.porder.status, "complete")

    def check_product_quantity(self, q):
        self.product = Product.objects.get(id=self.product.id)
        stocks = Stock.objects.filter(product=self.product)
        total = 0
        for s in stocks:
            total += s.quantity
        self.assertEqual(self.product.quantity, q)
        self.assertEqual(total, q)

    def create_sorder(self):
        data = {
            "concept": "Maintenance",
            "note": "Testing",
            "position": None,
            "storage_reason": "",
            "quotation": False,
            "parts_sale": False,
            "vin": "123123",
            "plate": "1234321",
            "invoice_data": "Just test",
        }
        form = S_OrderCreateForm(data=data)
        form.clean()
        self.assertTrue(form.is_valid(), form.errors)

        self.sorder = form.save(commit=False)
        self.sorder.type = "sell"
        self.sorder.created_by = self.user
        self.sorder.associated = self.associated
        self.sorder.save()

        self.assertIsNotNone(self.sorder)
        self.assertIsNotNone(self.sorder.id)

    def create_sorder_transaction(self):
        form = TransactionCreateForm(
            product=self.product,
            order=self.porder,
            data={
                "price": self.product.getSuggestedPrice(),
                "note": "Testing",
                "quantity": Quantity,
                "unit": self.product.unit,
                "tax": 8,
            },
        )
        self.assertTrue(form.is_valid(), form.errors)

        self.sorder_transaction: ProductTransaction = form.save(commit=False)
        self.sorder_transaction.order = self.sorder
        self.sorder_transaction.product = self.product
        self.sorder_transaction.save()

        self.assertIsNotNone(self.sorder_transaction)
        self.assertIsNotNone(self.sorder_transaction.id)

    def processing_sorter(self):
        handle_order_transactions(self.sorder)
        self.sorder.status = "processing"
        self.sorder.save()

        self.sorder = Order.objects.get(id=self.sorder.id)
        self.assertEqual(self.sorder.status, "processing")

    def decline_sorder(self):
        reverse_order_transactions(self.sorder)
        self.sorder.status = "decline"
        self.sorder.save()

        self.sorder = Order.objects.get(id=self.sorder.id)
        self.assertEqual(self.sorder.status, "decline")

    def test_all(self):
        # Tester
        self.create_user()
        # Provider and client
        self.create_provider()
        self.create_client()
        # Unit and product
        self.create_unit()
        self.create_product()
        # Check quantity
        self.check_product_quantity(0)

        # Order to increast the inventory
        self.create_porder()
        self.create_porder_transaction()

        # Order to decreast inventory
        self.create_sorder()
        self.create_sorder_transaction()

        for i in range(30):
            print(f"Iteration {i}")
            # Check quantity
            self.complete_porder()
            self.check_product_quantity(Quantity)
            # Multiple checks
            for j in range(10):
                print(f"    Porder {j}")
                # Check decline
                self.decline_porder()
                self.check_product_quantity(0)
                # Complete order again
                self.complete_porder()
                self.check_product_quantity(Quantity)
            # Check quantity
            self.processing_sorter()
            self.check_product_quantity(0)
            # Multiple checks
            for j in range(10):
                print(f"    Sorder {j}")
                # Check decline
                self.decline_sorder()
                self.check_product_quantity(Quantity)
                # Complete order again
                self.processing_sorter()
                self.check_product_quantity(0)
