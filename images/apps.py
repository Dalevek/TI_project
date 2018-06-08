# -*- coding: utf-8 -*-
from django.apps import AppConfig


class ImagesConfig(AppConfig):
    name = 'images'
    verbose_name = unicode('Dodawanie obrazów', "utf-8")

    def ready(self):
        import images.signals