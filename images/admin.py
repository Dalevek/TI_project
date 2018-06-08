# encoding=utf8
from django.contrib import admin
from .models import Image
from simple_history.admin import SimpleHistoryAdmin


class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'image', 'created']
    list_filter = ['created']


admin.site.register(Image, ImageAdmin)

