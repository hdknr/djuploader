from django.contrib import admin
from djuploader.admin import register


class ProfileAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'


register(__name__, globals())
