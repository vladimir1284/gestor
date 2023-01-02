from django.test import TestCase
from users.models import User, UserProfile


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
