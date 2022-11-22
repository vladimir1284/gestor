from urllib import response
from django.test import TestCase, Client
from django.contrib.auth.models import User
from datetime import datetime
from .forms import UnitCreateForm, ProductCreateForm
from .views import convertUnit, DifferentMagnitudeUnitsError
from .models import (
    Unit,
    Product,
    ProductCategory,
    Order,
    Profit,
    Transaction)
import random


class TestUnitConversion(TestCase):
    """
    This class contains tests that convert measurements from one
    unit of measurement to another.
    """

    def setUp(self):
        """
        This method runs before the execution of each test case.
        """
        self.client = Client()

        self.credentials = {
            'username': 'vladimir',
            'password': 'ganador'}
        User.objects.create_user(**self.credentials)
        # send login data
        response = self.client.post(
            '/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

        self.g_data = {
            'name': "g",
            'factor': "0.001",
            'magnitude': "mass",
        }
        self.kg_data = {
            'name': "kg",
            'factor': 1,
            'magnitude': "mass",
        }

    def test_unit_form(self):
        # g
        form = UnitCreateForm(data=self.g_data)
        self.assertTrue(form.is_valid())

    def test_unit_create(self):
        # kg (SI)
        self.client.post('/inventory/create-unit/', self.kg_data)
        kg = Unit.objects.get(name="kg")
        self.assertEqual(kg.factor, 1)

    def test_unit_convert(self):
        # g
        self.client.post('/inventory/create-unit/', self.g_data)

        # kg (SI)
        self.client.post('/inventory/create-unit/', self.kg_data)

        rand_g = random.uniform(1, 1000000000)
        calculated_kg = rand_g/1000.
        self.assertAlmostEqual(convertUnit(input_unit='g',
                                           output_unit='kg',
                                           value=rand_g), calculated_kg)

    def test_nonSI_unit_convert(self):
        # g
        self.client.post('/inventory/create-unit/', self.g_data)

        # lb
        lb_data = {
            'name': "lb",
            'factor': "{}".format(1/2.2),
            'magnitude': "mass",
        }
        self.client.post('/inventory/create-unit/', lb_data)

        rand_g = 1000
        calculated_lb = 2.2
        self.assertAlmostEqual(convertUnit(input_unit='g',
                                           output_unit='lb',
                                           value=rand_g), calculated_lb)

    def test_incompatible_unit_convert(self):
        # g
        self.client.post('/inventory/create-unit/', self.g_data)

        # km
        km_data = {
            'name': "km",
            'factor': "1000",
            'magnitude': "distance",
        }
        self.client.post('/inventory/create-unit/', km_data)

        rand_g = 1000
        try:
            convertUnit(input_unit='g',
                        output_unit='km',
                        value=rand_g)
        except DifferentMagnitudeUnitsError:
            return
        self.assertTrue(False)


class TestStockFIFO(TestCase):

    """
    Ejercicio resuelto de valoración de existencias (PMP-FIFO) 2.
    http://www.econosublime.com/2020/05/ejercicio-resuelto-pmp-fifo-valoracion-existencias.html
    """

    def setUp(self):
        """
        This method runs before the execution of each test case.
        """
        self.client = Client()

        self.credentials = {
            'username': 'testuser',
            'password': 'testpass'}
        User.objects.create_user(**self.credentials)
        # send login data
        response = self.client.post(
            '/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

    def test_fifo_exercise(self):
        # kg (SI)
        kg_data = {
            'name': "kg",
            'factor': 1,
            'magnitude': "mass",
        }
        self.client.post('/inventory/create-unit/', kg_data)

        # food
        food = {
            'name': "comida",
        }
        self.client.post('/inventory/create-category/', food)

        # supplier
        supplier = {
            'name': "Pedro Vendedor",
            'type': "supplier"
        }
        self.client.post('/users/create-provider/', supplier)

        # client
        client = {
            'name': "Juan Comprador",
            'type': "client"
        }
        self.client.post('/users/create-client/', client)

        # pescado congelado
        pescado_congelado = {
            'name': "pescado congelado",
            'unit': 1,
            'category': 1,
            'type': 'consumable',
            'sell_price': 20,
            'sell_tax': 15,
            'sell_price_min': 20,
            'sell_price_max': 30,
            'quantity_min': 30,

        }
        self.client.post('/inventory/create-product/', pescado_congelado)

        # 1 de enero inicial
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'inicial',
            'type': 'purchase',
            'associated': 1,
        }
        self.client.post('/inventory/create-order/', form_data)
        form_data = {
            'tax': 0,
            'price': 12,
            'unit': 1,
            'quantity': 100,
        }
        self.client.post('/inventory/create-transaction/1/1', form_data)
        trans = Transaction.objects.get(product=1)
        print(trans)
        self.client.post('/inventory/update-order-status/1/complete')
        product = Product.objects.get(id=1)
        self.assertEqual(product.quantity, 100)
        self.assertEqual(product.stock_price, 1200)

        # 4 de enero compra
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'compra',
            'type': 'purchase',
            'associated': 1,
        }
        self.client.post('/inventory/create-order/', form_data)
        form_data = {
            'product': 1,
            'tax': 0,
            'price': 14.25,
            'unit': 1,
            'quantity': 200,
        }
        self.client.post('/inventory/create-transaction/2/1', form_data)
        self.client.post('/inventory/update-order-status/2/complete')
        trans = Transaction.objects.get(price=14.25)
        print(trans)
        product = Product.objects.get(id=1)
        self.assertEqual(product.quantity, 300)
        self.assertEqual(product.stock_price, 1200+2850)

        # 8 de enero vende
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'venta',
            'type': 'sell',
            'associated': 2,
        }
        self.client.post('/inventory/create-order/', form_data)
        form_data = {
            'product': 1,
            'tax': 0,
            'price': 20,
            'unit': 1,
            'quantity': 150,
        }
        self.client.post('/inventory/create-transaction/3/1', form_data)
        self.client.post('/inventory/update-order-status/3/complete')
        trans = Transaction.objects.get(price=20)
        print(trans)
        product = Product.objects.get(id=1)
        self.assertEqual(product.quantity, 150)
        self.assertEqual(product.stock_price, 2137.5)
        profit = Profit.objects.all().order_by('-created_date')[0]
        print(profit)
        self.assertEqual(profit.profit, 1087.5)

        # 12 de enero compra
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'compra',
            'type': 'purchase',
            'associated': 1,
        }
        self.client.post('/inventory/create-order/', form_data)
        form_data = {
            'product': 1,
            'tax': 0,
            'price': 15,
            'unit': 1,
            'quantity': 225,
        }
        self.client.post('/inventory/create-transaction/4/1', form_data)
        self.client.post('/inventory/update-order-status/4/complete')
        trans = Transaction.objects.get(price=15)
        print(trans)
        product = Product.objects.get(id=1)
        self.assertEqual(product.quantity, 150+225)
        self.assertEqual(product.stock_price, 2137.5+3375)

        # 16 de enero vende
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'venta',
            'type': 'sell',
            'associated': 2,
        }
        self.client.post('/inventory/create-order/', form_data)
        form_data = {
            'product': 1,
            'tax': 0,
            'price': 30,
            'unit': 1,
            'quantity': 75,
        }
        self.client.post('/inventory/create-transaction/5/1', form_data)
        self.client.post('/inventory/update-order-status/5/complete')
        trans = Transaction.objects.get(price=30)
        print(trans)
        product = Product.objects.get(id=1)
        self.assertEqual(product.quantity, 75+225)
        self.assertEqual(product.stock_price, 1068.75+3375)
        profit = Profit.objects.all().order_by('-created_date')[0]
        print(profit)
        self.assertEqual(profit.profit, 1181.25)
