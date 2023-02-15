from django.test import TestCase
from users.models import User, UserProfile
from .views import getMonthYear
from datetime import date
from dateutil.relativedelta import relativedelta


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


class GetMonthYearTests(TestCase):

    def test_non_argument(self):
        (previous, current, next) = getMonthYear()
        now = date.today()
        self.assertEqual(current[0],  now.month)
        self.assertEqual(current[1], now.year)

        prev = now - relativedelta(months=1)
        self.assertEqual(previous[0], prev.month)
        self.assertEqual(previous[1], prev.year)

        foll = now + relativedelta(months=1)
        self.assertEqual(next[0], foll.month)
        self.assertEqual(next[1], foll.year)

    def test_january(self):
        (previous, current, next) = getMonthYear(1, 2023)
        self.assertEqual(current[0], 1)
        self.assertEqual(current[1], 2023)
        self.assertEqual(previous[0], 12)
        self.assertEqual(previous[1], 2022)
        self.assertEqual(next[0], 2)
        self.assertEqual(next[1], 2023)

    def test_december(self):
        (previous, current, next) = getMonthYear(12, 2022)
        self.assertEqual(current[0], 12)
        self.assertEqual(current[1], 2022)
        self.assertEqual(previous[0], 11)
        self.assertEqual(previous[1], 2022)
        self.assertEqual(next[0], 1)
        self.assertEqual(next[1], 2023)
