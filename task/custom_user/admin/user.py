from django.contrib import admin
from django.contrib.admin import register
from ..models import User


@register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'email', 'date_joined', 'is_active', 'is_email_verified')
    list_display_links = ('uuid',)
    search_fields = ('uuid', 'email',)
    list_editable = ('is_active', 'is_email_verified')
    save_on_top = True
