from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User

# class User(AbstractUser):
#     is_buyer = models.BooleanField(default=False)
#     is_supplier = models.BooleanField(default=False)
#     is_admin = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile_user')
    avatar = models.ImageField(upload_to='images/avatars')
    role = models.PositiveSmallIntegerField(
        choices=((1, 'Admin'),
                 (2, 'Mecánico')),
        default=1,
    )
    phone_number = PhoneNumberField(blank=True)

    def __str__(self):
        return self.user.get_username()
