from django.contrib import admin
from company.models import Company 
from googleoauth.models import OAuthUsers
import google.oauth2.credentials
import googleapiclient.discovery

class CompanyAdmin(admin.ModelAdmin):
    def create_company_folders(self,obj):
        credentials_dict = OAuthUsers.objects.get(status=True).get_credentials_dict()
        credentials = google.oauth2.credentials.Credentials(**credentials_dict)

        drive = googleapiclient.discovery.build(
          'drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': obj.name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = drive.files().create(body=file_metadata,fields='id').execute()

        folder_id = file.get('id')
        print ('Folder ID: %s' % file.get('id'))
        obj.folder_id = folder_id
        obj.save()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # create Google drive with folders
        self.create_company_folders(obj)
        
        
admin.site.register(Company, CompanyAdmin)
