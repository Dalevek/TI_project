# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from simple_history.models import HistoricalRecords
import redis
from django.conf import settings





#Połącz z baza danych Redis
r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
class Image(models.Model):
    #STATUS_CHOICES = (('draft', 'Roboczy'), ('published', 'Opublikowany'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='images_created')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField()

    image = models.ImageField(upload_to='images/%Y/%m/%d')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='images_liked', blank=True)
    total_likes = models.PositiveIntegerField(db_index=True, default=0)
    history = HistoricalRecords()


    def __unicode__(self):
        return self.title
    #def __str__(self):
    #    return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Image, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('images:detail', args=[self.id, self.slug])

