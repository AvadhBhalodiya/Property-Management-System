from django.contrib import admin

from apps.properties.models import Property, Unit

admin.site.register(Property)
admin.site.register(Unit)
