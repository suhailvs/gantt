from django.db import models
import json 
from django.conf import settings

# Create your models here.
class GoogleOAuth(models.Model):
    """Only 1 item is active at a time"""
    name = models.CharField(max_length=200, default='Test Credentials')
    # you can get this file from https://console.developers.google.com
    # put files in googleoauth/client_secret_json/ folder
    client_secret_filename = models.CharField(max_length=200, default='client_secret_1.json') 
    redirect_uri = models.CharField(max_length=200, default='')
    # ["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.file"]
    scopes = models.TextField(default = '["https://www.googleapis.com/auth/spreadsheets.readonly","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.file"]')    
    client_id = models.TextField()
    client_secret =  models.TextField()
    status = models.BooleanField(default=True)
    
    def get_scopes(self):
        return json.loads(self.scopes)


class OAuthUsers(models.Model):
    name = models.CharField(max_length=200, default='Test Credentials')
    token = models.TextField(blank=True)
    refresh_token =  models.TextField(blank=True)
    token_uri =  models.TextField(blank=True)
    client_id = models.TextField()
    client_secret =  models.TextField()
    scopes = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    
    def get_scopes(self):
        return json.loads(self.scopes)

    def get_credentials_dict(self):
        return {
            'token': self.token,
            'refresh_token': self.refresh_token,
            'token_uri': self.token_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scopes': self.get_scopes()
        }

    def __str__(self):
        return f'{self.name}({self.status})'