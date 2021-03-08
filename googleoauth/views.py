import os, json
import google_auth_oauthlib.flow

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib import messages
from django.views import View
from django.http import HttpResponse, JsonResponse

from googleoauth.models import GoogleOAuth, OAuthUsers


class CredentialsListView(LoginRequiredMixin, ListView):
    model = GoogleOAuth

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
            # deactivate all oauthusers
            OAuthUsers.objects.all().update(status=False)
            OAuthUsers.objects.create(
                owner = request.user,
                token =credentials.token,
                refresh_token = credentials.refresh_token or '',
                token_uri= credentials.token_uri,
                client_id= credentials.client_id,
                client_secret= credentials.client_secret,
                scopes= json.dumps(credentials.scopes),
                status = True)
        return redirect('company:get_files')

