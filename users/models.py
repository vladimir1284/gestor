from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image


class Contact(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=120)
    alias = models.CharField(_("Local alias"), max_length=120,
                             null=True, blank=True)
    LANG_CHOICE = (
        ('spanish', 'Spanish'),
        ('english', 'English'),
    )
    language = models.CharField(_('Language'), max_length=20,
                                choices=LANG_CHOICE, default='spanish')
    active = models.BooleanField(default=True)
    membership = models.BooleanField(default=False)
    STATE_CHOICE = (
        ('florida', 'Florida'),
        ('texas', 'Texas'),
        ('other', 'Other'),
    )
    state = models.CharField(
        max_length=20, choices=STATE_CHOICE, default='texas')
    other_state = models.CharField(_('State'), max_length=20, blank=True)
    CITY_CHOICE = (
        ('houston', 'Houston'),
        ('dallas', 'Dallas'),
        ('austin', 'Austin'),
        ('san_antonio', 'San Antonio'),
        ('miami', 'Miami'),
        ('tampa', 'Tampa'),
        ('orlando', 'Orlando'),
        ('jacksonville', 'Jacksonville'),
        ('other', 'Other'),
    )
    city = models.CharField(
        max_length=20, choices=CITY_CHOICE, default='houston')
    other_city = models.CharField(_('City'), max_length=20, blank=True)
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
    VEHICLES_CHOICE = (
        ('1', '1'),
        ('2-5', '2-5'),
        ('>5', '>5'),
    )
    vehicles = models.CharField(_('Number of vehicles'), max_length=20,
                                choices=VEHICLES_CHOICE, default='1')


class Associated(Contact):
    # Either client or provider
    TYPE_CHOICE = (
        ('client', _('Client')),
        ('provider', _('provider')),
    )
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICE, default='client')
    license = models.CharField(max_length=50, blank=True, null=True)
    # Provides third party expense
    outsource = models.BooleanField(_('Outsource'), default=False)
    debt = models.FloatField(default=0)


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
