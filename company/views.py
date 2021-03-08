
import os, json
import pandas as pd
import numpy as np

import google.oauth2.credentials
import googleapiclient.discovery

from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from googleoauth.models import OAuthUsers


class GetFilesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        credentials = OAuthUsers.objects.filter(status=True).first()
        if not credentials:
            # if google account not connected, show google login
            return redirect('googleoauth:login')

        
        credentials = google.oauth2.credentials.Credentials(**credentials.get_credentials_dict())
        drive = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)
        files = drive.files().list().execute()
        return render(request, 'company/files.html',{'files':files})


class GoogleChartView(LoginRequiredMixin, View):
    def get_spreadsheet_api(self, user):
        credentials = OAuthUsers.objects.get(owner = user)
        credentials = google.oauth2.credentials.Credentials(**credentials.get_credentials_dict())
        sheets = googleapiclient.discovery.build( 'sheets', 'v4', credentials=credentials)
        return sheets.spreadsheets()

    def date_to_str(self, date):
        try: 
            return date.strftime("%Y-%m-%dT%H:%M:%S%z")
        except:
            return None

    def blank_to_none(self, items):
        new = []
        for sub_items in items:
            row = []
            for item in sub_items:
                row.append(None if item == '' else item)
            new.append(row)
        return new

    def get_spreadsheet_data(self, sheet, sheet_id, sheet_range='!A2:G'):
        result = sheet.values().get(spreadsheetId=sheet_id,range=sheet_range).execute()
        values = result.get('values', [])
        
        columns = ['id', 'name', 'dependencies', 'sdate','edate', 'duration', 'progress']
        df = pd.DataFrame(np.array(values), columns=columns)
        
        df['sdate'] = pd.to_datetime(df['sdate']).apply(lambda x: self.date_to_str(x))
        df['edate'] = pd.to_datetime(df['edate']).apply(lambda x: self.date_to_str(x))
        df['progress'] = df['progress'].str.replace(r'\D', '').astype(int)

        df=df.reindex(columns=['id', 'name', 'sdate','edate', 'duration', 'progress','dependencies'])

        items = df.values.tolist() #list(df.values) #df.values.tolist()

        return self.blank_to_none(items)

    def post(self, request):
        # update cell in google sheet
        # 'row': ['3'], 'column_name': ['progress'], 'data': ['1']
        row = int(request.POST['row'])+2 # skip Heading and make it start from 1
        column= request.POST['column_name']
        data = request.POST['data']
        columns={'id':'A', 'name':'B', 'dependencies':'C','sdate':'D','edate':'E', 'duration':'F', 
            'progress':'G'}

        sheet_range = f'!{columns[column]}{row}'
        body = {
            'values': [[data]]
        }
        sheet = self.get_spreadsheet_api(request.user)
        result = sheet.values().update(
            spreadsheetId=request.POST['sheet_id'], range=sheet_range,
            valueInputOption='RAW', body=body).execute()

        items = self.get_spreadsheet_data(sheet,request.POST['sheet_id'])
        return JsonResponse(items, safe=False)

    def get(self, request):
        sheet = self.get_spreadsheet_api(request.user)
        items = self.get_spreadsheet_data(sheet,request.GET['sheet_id'])
        # items2 = [["Research","Find sources","2014-12-31T18:30:00.000Z","2015-01-04T18:30:00.000Z",None,100,None],]
        return render(request, 'company/googlechart.html', {'items':json.dumps(items)}) # 'tasks':df.id.tolist()})