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
    Transaction,
    Associated)
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
            '/users/login/?next=/users/create-user/', self.credentials, follow=True)
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
        self.client.post('/store/create-unit/', self.kg_data)
        kg = Unit.objects.get(name="kg")
        self.assertEqual(kg.factor, 1)

    def test_unit_convert(self):
        # g
        self.client.post('/store/create-unit/', self.g_data)

        # kg (SI)
        self.client.post('/store/create-unit/', self.kg_data)

        rand_g = random.uniform(1, 1000000000)
        calculated_kg = rand_g/1000.
        self.assertAlmostEqual(convertUnit(input_unit='g',
                                           output_unit='kg',
                                           value=rand_g), calculated_kg)

    def test_nonSI_unit_convert(self):
        # g
        self.client.post('/store/create-unit/', self.g_data)

        # lb
        lb_data = {
            'name': "lb",
            'factor': "{}".format(1/2.2),
            'magnitude': "mass",
        }
        self.client.post('/store/create-unit/', lb_data)

        rand_g = 1000
        calculated_lb = 2.2
        self.assertAlmostEqual(convertUnit(input_unit='g',
                                           output_unit='lb',
                                           value=rand_g), calculated_lb)

    def test_incompatible_unit_convert(self):
        # g
        self.client.post('/store/create-unit/', self.g_data)

        # km
        km_data = {
            'name': "km",
            'factor': "1000",
            'magnitude': "distance",
        }
        self.client.post('/store/create-unit/', km_data)

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
            '/users/login/?next=/users/create-user/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

    def test_initial_stock(self):
        # kg (SI)
        kg_data = {
            'name': "kg",
            'factor': 1,
            'magnitude': "mass",
        }
        self.client.post('/store/create-unit/', kg_data)

        # food
        food = {
            'name': "comida",
        }
        self.client.post('/store/create-category/', food)

        # supplier
        supplier = {
            'name': "Pedro Vendedor",
            'type': "supplier",
        }
        self.client.post('/store/create-associated/', supplier)

        # client
        client = {
            'name': "Juan Comprador",
            'type': "client",
        }
        self.client.post('/store/create-associated/', client)

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
        self.client.post('/store/create-product/', pescado_congelado)

        # 1 de enero inicial
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'inicial',
            'type': 'purchase',
            'associated': 1,
            'form-0-product': 1,
            'form-0-tax': 0,
            'form-0-price': 12,
            'form-0-unit': 1,
            'form-0-quantity': 100,
        }
        self.client.post('/store/create-order/', form_data)
        trans = Transaction.objects.get(product=1)
        print(trans)
        self.assertEqual(trans.quantity, 100)

        # 4 de enero compra
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'compra',
            'type': 'purchase',
            'associated': 1,
            'form-0-product': 1,
            'form-0-tax': 0,
            'form-0-price': 14.5,
            'form-0-unit': 1,
            'form-0-quantity': 200,
        }
        self.client.post('/store/create-order/', form_data)
        trans = Transaction.objects.get(price=14.5)
        print(trans)
        self.assertEqual(trans.quantity, 200)

        # 8 de enero vende
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'venta',
            'type': 'sell',
            'associated': 2,
            'form-0-product': 1,
            'form-0-tax': 0,
            'form-0-price': 20,
            'form-0-unit': 1,
            'form-0-quantity': 150,
        }
        self.client.post('/store/create-order/', form_data)
        trans = Transaction.objects.get(price=20)
        print(trans)
        self.assertEqual(trans.quantity, 150)

        # 12 de enero compra
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'compra',
            'type': 'purchase',
            'associated': 1,
            'form-0-product': 1,
            'form-0-tax': 0,
            'form-0-price': 15,
            'form-0-unit': 1,
            'form-0-quantity': 225,
        }
        self.client.post('/store/create-order/', form_data)
        trans = Transaction.objects.get(price=15)
        print(trans)
        self.assertEqual(trans.quantity, 225)

        # 16 de enero vende
        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'concept': 'venta',
            'type': 'sell',
            'associated': 2,
            'form-0-product': 1,
            'form-0-tax': 0,
            'form-0-price': 30,
            'form-0-unit': 1,
            'form-0-quantity': 75,
        }
        self.client.post('/store/create-order/', form_data)
        trans = Transaction.objects.get(price=30)
        print(trans)
        self.assertEqual(trans.quantity, 75)
