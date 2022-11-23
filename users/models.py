from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image


class Associated(models.Model):
    # Either client or supplier
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    note = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    AVATAR_SIZE = 100
    avatar = models.ImageField(upload_to='images/avatars/',
                               blank=True)
    phone_number = PhoneNumberField(blank=True)
    TYPE_CHOICE = (
        ('client', _('Client')),
        ('supplier', _('Supplier')),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICE,
                            default='client')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Associated, self).save(*args, **kwargs)
        try:
            img = Image.open(self.avatar.path)

            if img.height > self.AVATAR_SIZE or img.width > self.AVATAR_SIZE:
                output_size = (self.AVATAR_SIZE, self.AVATAR_SIZE)
                img.thumbnail(output_size)
            img.save(self.avatar.path)
        except Exception as error:
            print(error)


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile_user')
    avatar = models.ImageField(upload_to='images/avatars',
                               blank=True)
    role = models.PositiveSmallIntegerField(
        choices=((1, 'Admin'),
                 (2, 'Mecánico')),
        default=1,
    )
    phone_number = PhoneNumberField(blank=True)

    def __str__(self):
        return self.user.get_username()
