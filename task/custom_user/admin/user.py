from django.contrib import admin
from django.contrib.admin import register
from ..models import User

@register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'email', 'date_joined', 'is_active')
    list_display_links = ('uuid',)
