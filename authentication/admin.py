from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# class UserAdmin(admin.ModelAdmin):
#     search_fields = ('username', )

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        ('User Type', {'fields': ('user_type',)}),
        ('Company', {'fields': ('company',)})
    )

admin.site.register(get_user_model(), CustomUserAdmin)