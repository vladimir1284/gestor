from django.test import TestCase
from .models import Cost, CostCategory
from users.models import User, UserProfile
from datetime import date


class BaseModelTests(TestCase):
    def setUp(self):
        """
        This method runs before the execution of each test case.
        """

        self.credentials = {
            'username': 'myuser',
            'password': 'mypass'}
        user = User.objects.create_user(**self.credentials)
        UserProfile.objects.create(user=user)
        # send login data
        response = self.client.post(
            '/users/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)


class CostModelTests(BaseModelTests):
    def test_cost_model(self):
        # Create a user
        user = User.objects.create(username='testuser')
        # Create a cost category
        category = CostCategory.objects.create(name='Test Category')
        # Create a cost
        cost = Cost.objects.create(
            concept='Test Cost',
            note='This is a test',
            date=date(2020, 1, 1),
            category=category,
            amount=500.00,
            created_by=user,
            related_to=user
        )
        # Check that the cost was created correctly
        self.assertEqual(cost.concept, 'Test Cost')


class CostListTests(BaseModelTests):
    def setUp(self):
        super(CostListTests, self).setUp()

        # Create a user
        user = User.objects.create(username='testuser')

        # Create a cost category
        category = CostCategory.objects.create(name='Test Category')

        # Create some test objects
        Cost.objects.create(
            concept='Test Cost',
            note='This is a test',
            date=date(2020, 1, 1),
            category=category,
            amount=500.00,
            created_by=user
        )
        Cost.objects.create(
            concept='Test Cost',
            note='This is a test',
            date=date(2020, 1, 15),
            category=category,
            amount=1000.00,
            created_by=user
        )
        Cost.objects.create(
            concept='Test Cost',
            note='This is a test',
            date=date(2020, 2, 1),
            category=category,
            amount=1500.00,
            created_by=user
        )

    def test_start_end(self):
        # Make the request
        response = self.client.get('/costs/list-cost/', {
            'start_date': date(2020, 1, 10),
            'end_date': date(2020, 1, 20)
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['costs']), 1)

    def test_start(self):
        # Make the request
        response = self.client.get('/costs/list-cost/', {
            'start_date': date(2020, 1, 10)
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['costs']), 2)

    def test_end(self):
        # Make the request
        response = self.client.get('/costs/list-cost/', {
            'end_date': date(2020, 1, 20)
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['costs']), 2)

    def test_cost_list(self):
        # Make the request
        response = self.client.get('/costs/list-cost/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['costs']), 3)
