from django.contrib import admin

from . import models


admin.site.register(models.Thing)
admin.site.register(models.Item)
admin.site.register(models.Document)
admin.site.register(models.Previous_date)