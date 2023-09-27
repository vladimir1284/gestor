from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rent.models.lease import Lease, Payment, Due, Contract, LesseeData
from rent.models.vehicle import Trailer, Manufacturer
from users.models import Associated, UserProfile
from django.test import Client


class PaymentViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.credentials = {
            'username': 'myuser',
            'password': 'mypass'}
        self.user = User.objects.create_user(**self.credentials)
        UserProfile.objects.create(user=self.user)
        # send login data
        response = self.client.post(
            '/erp/users/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

        self.lessee = Associated.objects.create(name='Test Client')
        LesseeData.objects.create(
            associated=self.lessee,
            contact_name="Test contact",
            contact_phone="+1304233456",
            license_number="test license",
            client_address="testclient address",
        )
        effective_date = (timezone.now() - timedelta(weeks=5)).date()
        print(f"Effective date: {effective_date}")
        self.contract = Contract.objects.create(
            effective_date=effective_date,
            payment_amount=100,
            lessee=self.lessee,
            security_deposit=1000,
            stage='active',
            trailer=Trailer.objects.create(
                type='flatbed',
                axis_number=1,
                load=7,
                year=2020,
                cdl=False,
                manufacturer=Manufacturer.objects.create(
                    brand_name="Test Trailers",
                    url="http://testtrailers.com"
                )
            ))
        self.lease = Lease.objects.create(
            contract=self.contract,
            payment_frequency='weekly',
            payment_amount=100,
            num_due_payments=0,
            user=self.user
        )
        self.payment_url = reverse('rental-payment', args=[self.lessee.id])

    def test_payment_view_with_valid_payment(self):
        # Create a valid payment form data
        form_data = {
            'amount': 100,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Make a POST request to the payment view with the valid form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment was processed and redirected to the client detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'client-detail', args=[self.lessee.id]))

        # Check if the payment and due instances were created correctly
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Due.objects.count(), 1)

    def test_payment_view_with_invalid_payment(self):
        # Create an invalid payment form data
        form_data = {
            'amount': -100,  # Negative amount is invalid
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        response = self.client.post('/erp/users/login/', follow=True,
                                    username='testuser', password='testpassword')
        self.assertTrue(response.context['user'].is_active)

        # Make a POST request to the payment view with the invalid form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the form is rendered again with validation errors
        self.assertEqual(response.status_code, 200)
        # self.assertFormError(response, 'form', 'amount',
        #                      'Amount cannot be negative.')

        # Check that no payment or due instances were created
        self.assertEqual(Payment.objects.count(), 0)
        self.assertEqual(Due.objects.count(), 0)

    def test_payment_view_without_previous_payment_and_due_double_amount(self):
        # Create a payment form data
        form_data = {
            'amount': 200,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Make a POST request to the payment view with the form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment and due instances were created correctly
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Due.objects.count(), 2)

    def test_payment_view_with_previous_payment_and_due(self):
        # Create a previous payment and due instances
        previous_payment = Payment.objects.create(
            date_of_payment=timezone.now().date(),
            remaining=0,
            amount=100, client=self.lessee, lease=self.lease,
            user=self.user)
        Due.objects.create(date=timezone.now().date(),
                           amount=100, client=self.lessee, lease=self.lease)

        # Create a payment form data
        form_data = {
            'amount': 200,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Make a POST request to the payment view with the form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment and due instances were created correctly
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Payment.objects.count(), 2)
        self.assertEqual(Due.objects.count(), 3)

    def test_payment_view_with_previous_payment_remaining(self):
        # Create a previous payment and due instances
        previous_payment = Payment.objects.create(
            date_of_payment=timezone.now().date(),
            remaining=10,
            amount=100, client=self.lessee, lease=self.lease,
            user=self.user)
        Due.objects.create(date=timezone.now().date(),
                           amount=100, client=self.lessee, lease=self.lease)

        # Create a payment form data
        form_data = {
            'amount': 120,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Make a POST request to the payment view with the form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment and due instances were created correctly
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Payment.objects.count(), 2)
        self.assertEqual(Payment.objects.last().remaining, 30)
        self.assertEqual(Due.objects.count(), 2)

    def test_payment_view_with_remaining(self):
        # Create a valid payment form data
        form_data = {
            'amount': 320,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Make a POST request to the payment view with the valid form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment was processed and redirected to the client detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'client-detail', args=[self.lessee.id]))

        # Check if the payment and due instances were created correctly
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.last().remaining, 20)
        self.assertEqual(Due.objects.count(), 3)
        for due in Due.objects.all():
            print(f"Due date: {due.date}")

    def test_payment_view_with_too_low_amount(self):
        # Create a valid payment form data
        form_data = {
            'amount': 56,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Make a POST request to the payment view with the valid form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment was processed and redirected to the client detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'client-detail', args=[self.lessee.id]))

        # Check if the payment and due instances were created correctly
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.last().remaining, 56)
        self.assertEqual(Due.objects.count(), 0)
