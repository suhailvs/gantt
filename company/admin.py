from django.contrib import admin
from company.models import Company 
from googleoauth.models import OAuthUsers
import google.oauth2.credentials
import googleapiclient.discovery

from .views import get_credentials

class CompanyAdmin(admin.ModelAdmin):
    def get_body(self, name, parent=None):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent:
            file_metadata['parents'] = [parent]
        return file_metadata

    def create_spreadsheet(self, drive, name, parent):
        file_metadata = {
            'name': name,
            'parents': [parent],
            'mimeType': 'application/vnd.google-apps.spreadsheet',
        }
        spreadsheet = drive.files().create(body=file_metadata, fields='id').execute()
        return spreadsheet

    def create_company_folders(self,obj):
        drive = get_credentials()
        # create company root folder
        file = drive.files().create(body=self.get_body(obj.name),fields='id').execute()
        # save folder id so that it can be displayed to other user types
        obj.folder_id = file.get('id')
        obj.save()

        database_folder_id = ''
        # create sub folders
        for folder in ['Database', 'Masters', 'Users']:
            file = drive.files().create(body=self.get_body(folder,obj.folder_id),fields='id').execute()
            if folder=='Database': database_folder_id=file.get('id')

        # create google spreadsheets inside Database folder
        
        milestone_sheet = self.create_spreadsheet(drive,'Milestone-database',database_folder_id)
        task_sheet = self.create_spreadsheet(drive,'Task Database',database_folder_id)
        obj.milestone_sheet_id = milestone_sheet.get('id')
        obj.task_sheet_id = task_sheet.get('id')
        obj.save()
       


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # create Google drive with folders
        self.create_company_folders(obj)
        
        
admin.site.register(Company, CompanyAdmin)
