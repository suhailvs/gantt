import os, json
import google_auth_oauthlib.flow
# import requests

import google.oauth2.credentials
import googleapiclient.discovery

from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy
from django.http import HttpResponse

from googleoauth.models import GoogleOAuth, OAuthUsers


class CredentialsListView(LoginRequiredMixin, ListView):
    model = GoogleOAuth

# class CredentialsUpdateView(UpdateView):
#     model = GoogleOAuth
#     fields = '__all__'
#     template_name = 'googleoauth/credentials_update_form.html'
#     success_url = reverse_lazy('googleoauth:credential_list')

class CredentialsCreateView(LoginRequiredMixin, CreateView):
    model = GoogleOAuth
    fields = ['name','client_secret_filename','redirect_uri','scopes','client_id','client_secret']

    def form_valid(self, form):
        GoogleOAuth.objects.all().update(status=False)
        form.save()
        messages.success(self.request, 'The credentials was created with success!')
        return redirect('googleoauth:credential_list')

class GoogleAuthView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        cred = GoogleOAuth.objects.filter(status=True).first()

        if not cred:
            return HttpResponse('no credentials found')

        # you can get this file from https://console.developers.google.com
        CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR,'googleoauth','client_secret_json',cred.client_secret_filename)

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=cred.get_scopes())

        flow.redirect_uri = cred.redirect_uri
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        # Store the state so the callback can verify the auth server response.
        request.session['state'] = state
        return redirect(authorization_url)

#https://developers.google.com/identity/protocols/oauth2/web-server#python_1
class OAuth2CallbackView(View):

    def get(self, request, *args, **kwargs):
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        cred = GoogleOAuth.objects.filter(status=True).first()
        CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR,'googleoauth','client_secret_json',cred.client_secret_filename)


        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
          CLIENT_SECRETS_FILE, scopes=cred.get_scopes(), state = request.session['state'])
        flow.redirect_uri = cred.redirect_uri

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.build_absolute_uri() # request.get_full_path()
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        credentials = flow.credentials
        if credentials:
            OAuthUsers.objects.filter(owner=request.user).delete()
            OAuthUsers.objects.create(
                owner = request.user,
                token =credentials.token,
                refresh_token = credentials.refresh_token or '',
                token_uri= credentials.token_uri,
                client_id= credentials.client_id,
                client_secret= credentials.client_secret,
                scopes= json.dumps(credentials.scopes))
        return redirect('googleoauth:get_files')

class GetFilesView(View):
    def get(self, request, *args, **kwargs):
        credentials = OAuthUsers.objects.filter(owner = request.user).first()
        if not credentials:
            # if google account not connected, show google login
            return redirect('googleoauth:login')

        credentials_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.get_scopes()
        }

        credentials = google.oauth2.credentials.Credentials(**credentials_dict)
        API_SERVICE_NAME = 'drive'
        API_VERSION = 'v3'

        drive = googleapiclient.discovery.build(
          API_SERVICE_NAME, API_VERSION, credentials=credentials)
        files = drive.files().list().execute()

        return render(request, 'googleoauth/files.html',{'files':files})

def get_spreadsheet(user,sheet_id):
    credentials = OAuthUsers.objects.get(owner = user)
    credentials_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.get_scopes()
    }

    credentials = google.oauth2.credentials.Credentials(**credentials_dict)

    drive = googleapiclient.discovery.build(
      'sheets', 'v4', credentials=credentials)

    sheet = drive.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                            range='!A2:G').execute()

    return result.get('values', [])



class SpreadSheetView(View):
    def get(self, request):
        sheet_id = request.GET['sheet_id']
        values = get_spreadsheet(request.user, sheet_id)

        if not values:
            return HttpResponse('No data')
 
        return render(request, 'googleoauth/sheet.html',{'values':values})


class GoogleChartView(View):
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

    def get(self, request):
        values = get_spreadsheet(request.user, request.GET['sheet_id'])

        import pandas as pd
        import numpy as np

        columns = ['id', 'name', 'dependencies', 'sdate','edate', 'duration', 'progress']
        df = pd.DataFrame(np.array(values), columns=columns)
        
        df['sdate'] = pd.to_datetime(df['sdate']).apply(lambda x: self.date_to_str(x))
        df['edate'] = pd.to_datetime(df['edate']).apply(lambda x: self.date_to_str(x))
        df['progress'] = df['progress'].str.replace(r'\D', '').astype(int)
        # df['duration'] = df['duration'].fillna(None) #.astype(int)
        # df[list("ABCD")] = df[list("ABCD")].astype(int)

        df=df.reindex(columns=['id', 'name', 'sdate','edate', 'duration', 'progress','dependencies'])
        # df.fillna(0, inplace=True)
        # df = df.replace(r'^\s*$', None, regex=True)

        items = df.values.tolist() #list(df.values) #df.values.tolist()

        items = self.blank_to_none(items)

        
        # 'Task ID', 'Task Name', 'Start Date', 'End Date', 'Duration', 'Percent Complete', 'Dependencies'
        # items2 = [["Research","Find sources","2014-12-31T18:30:00.000Z","2015-01-04T18:30:00.000Z",None,100,None],["Write","Write paper",None,"2015-01-08T18:30:00.000Z",259200000,25,"Research,Outline"],["Cite","Create bibliography",None,"2015-01-06T18:30:00.000Z",86400000,20,"Research"],["Complete","Hand in paper",None,"2015-01-09T18:30:00.000Z",86400000,0,"Cite,Write"],["Outline","Outline paper",None,"2015-01-05T18:30:00.000Z",86400000,100,"Research"]]
        return render(request, 'googleoauth/googlechart.html', {'items':json.dumps(items)})
# GoogleChartView