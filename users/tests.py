from django.test import TestCase, Client
from .models import User, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import UserCreateForm, UserProfileForm


class TestUserManagement(TestCase):
    """
    This class contains tests that convert measurements from one
    unit of measurement to another.
    """
    def setUp(self):
        """
        This method runs before the execution of each test case.
        """
        self.client = Client()

    def test_UserCreate_form(self):
        post_dict = {
            'username': "ariel", 
            'password1': "SeS@m084",
            'password2': "SeS@m084",
            'first_name':"Ariel", 
            'last_name':"Casanova",  
            'email': 'towithouston@gmail.com',
        }
        form = UserCreateForm(data=post_dict)
        self.assertTrue(form.is_valid())

    def test_UserProfile_form(self):
        upload_file = open('/home/vladimir/Pictures/3ba3cfdb592c08cea6c0de2ea659ba0a.gif', 'rb')
        post_dict = {'role': "1"}
        file_dict = {'avatar': SimpleUploadedFile(upload_file.name, upload_file.read()),}
        form = UserProfileForm(post_dict, file_dict)
        self.assertTrue(form.is_valid())

    def test_create_user(self):
        with open('/home/vladimir/Pictures/3ba3cfdb592c08cea6c0de2ea659ba0a.gif', 'rb') as fp:
            self.client.post('/users/create-user/', {
                'first_name':"Ariel", 
                'last_name':"Casanova", 
                'username': "ariel", 
                'password1': "SeS@m084",
                'password2': "SeS@m084",
                'email': 'towithouston@gmail.com',
                'role': 1,
                'avatar': fp})
        self.assertEqual(User.objects.last().username, "ariel")