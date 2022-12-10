from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image
import uuid


class Contact(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    address = models.TextField(blank=True)
    note = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    AVATAR_SIZE = 100
    avatar = models.ImageField(upload_to='images/avatars/',
                               blank=True)
    phone_number = PhoneNumberField(blank=True)

    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)
        try:
            img = Image.open(self.avatar.path)

            if img.height > self.AVATAR_SIZE or img.width > self.AVATAR_SIZE:
                output_size = (self.AVATAR_SIZE, self.AVATAR_SIZE)
                img.thumbnail(output_size)
            img.save(self.avatar.path)
        except Exception as error:
            print(error)

    def __str__(self):
        return self.name


class Company(Contact):
    class Meta:
        abstract = False
    id = models.SlugField(primary_key=True, unique=True, default=uuid.uuid1)


class Associated(Contact):
    # Either client or provider
    company = models.ForeignKey(Company,
                                on_delete=models.SET_NULL,
                                blank=True, null=True)
    TYPE_CHOICE = (
        ('client', _('Client')),
        ('provider', _('provider')),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICE,
                            default='client')


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
