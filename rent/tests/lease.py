from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rent.models.lease import Lease, Payment, Due, Contract, LesseeData
from rent.models.vehicle import Trailer, Manufacturer
from users.models import Associated, UserProfile
from django.test import Client


class LeaseUpdateTests(TestCase):
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
        self.effective_date = (timezone.now() - timedelta(weeks=5)).date()
        print(f"Effective date: {self.effective_date}")
        self.contract = Contract.objects.create(
            effective_date=self.effective_date,
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

    def test_lease_update_amount(self):
        # Create a valid payment form data
        form_data = {
            'amount': 100,
            'lease': self.lease.id,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Check the covered date without payment
        self.lease.compute_payment_cover()
        self.assertEqual(self.lease.last_payment_cover, None)

        # Make a POST request to the payment view with the valid form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment was processed and redirected to the client detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'client-detail', args=[self.lessee.id]))

        # Check if the payment and due instances were created correctly
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Due.objects.count(), 1)

        # Check the covered date after one payment
        self.lease.compute_payment_cover()
        self.assertEqual(self.lease.last_payment_cover,
                         self.effective_date+timedelta(days=8))

        # Revert payment
        revert_url = reverse(
            'revert-payment', args=[Payment.objects.last().id])

        # Make the revert request
        response = self.client.get(revert_url)

        # Check if the payment was processed and redirected to the client detail page
        self.assertEqual(response.status_code, 302)

        # Check if the payment and due instances were deleted correctly
        self.assertEqual(Payment.objects.count(), 0)
        self.assertEqual(Due.objects.count(), 0)

    def test_closing_contract(self):
        # Create a valid payment form data
        form_data = {
            'amount': 200,
            'lease': self.lease.id,
            'date_of_payment': timezone.now().date()
        }

        # Login the user
        self.client.post('/erp/users/login/', follow=True,
                         username='testuser', password='testpassword')

        # Check the covered date without payment
        self.lease.compute_payment_cover()
        self.assertEqual(self.lease.last_payment_cover, None)

        # Make a POST request to the payment view with the valid form data
        response = self.client.post(self.payment_url, data=form_data)

        # Check if the payment was processed and redirected to the client detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'client-detail', args=[self.lessee.id]))

        # Check if the payment and due instances were created correctly
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Due.objects.count(), 2)

        # Check the covered date after one payment
        self.lease.compute_payment_cover()
        self.assertEqual(self.lease.last_payment_cover,
                         self.effective_date+timedelta(days=15))

        # Close the contract
        close_url = f'/erp/rent/update_contract_stage/{self.contract.id}/ended'
        response = self.client.get(close_url)

        # Check if the payment was processed and redirected to the client detail page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Contract.objects.get(
            id=self.contract.id).ended_date, timezone.now().date())
        self.assertEqual(Contract.objects.get(
            id=self.contract.id).final_debt, 400)
