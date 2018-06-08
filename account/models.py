# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    history = HistoricalRecords()

    def __unicode__(self):
        return 'Profil uzytkownika {}'.format(self.user.username)


class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set')
    user_to = models.ForeignKey(User, related_name='rel_to_set')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)


#Dynamiczne dodanie ponizszej kolumny do modelu User
User.add_to_class('following',
                  models.ManyToManyField('self',
                                         through=Contact,
                                         related_name='followers',
                                         symmetrical=False))



