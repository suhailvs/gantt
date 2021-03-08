from django.contrib import admin

# Register your models here.
from .models import GoogleOAuth, OAuthUsers

admin.site.register(GoogleOAuth)
admin.site.register(OAuthUsers)