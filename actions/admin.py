from django.contrib import admin
from .models import Action
from simple_history.admin import SimpleHistoryAdmin


class ActionAdmin(admin.ModelAdmin):
    list_filter = ('created',)
    list_display = ('user', 'verb', 'target', 'created')
    search_fields = ('verb',)

admin.site.register(Action, ActionAdmin)
