# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import http.client
from django.http import HttpResponse
# import os
# import datetime
# from django.conf import settings
from django.utils import timezone
from django.views import View


from projects.models import GoogleDriveAuth
from django.contrib.auth.mixins import LoginRequiredMixin

def generate_access_token(account_settings):
    try:
        conn = http.client.HTTPSConnection("oauth2.googleapis.com")
        payload = ''
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
        conn.request("POST", "/token?client_id="+account_settings.client_id+"&client_secret="+account_settings.client_secret+"&refresh_token="+account_settings.refresh_token+"&grant_type=refresh_token", payload, headers)
        res = conn.getresponse()
        data = res.read()
    except:
        return "error_of_geting_token"
    try:
        response = json.loads(data.decode("utf-8"))
    except:
        return "error_on_getting_data"
    try:
        GoogleDriveAuth.objects.filter(id=account_settings.id).update(
                access_token = response['access_token'],
                token_expiry_time=response['expires_in'],
                token_id = response['id_token']
                )
    except:
        return "error_of_geting_token"
    return 'success'


def getGoogleSheets(method,payload,event_id, get_list=True):
    # createCalenderEvent
    account_settings = GoogleDriveAuth.objects.filter(status=True).first()
    difference = timezone.now() - account_settings.token_start_time;  
    difference = int(difference.total_seconds());
    if difference >= account_settings.token_expiry_time:
        resp = generate_access_token(account_settings)
        if resp =='error_of_geting_token' or resp =='error_on_getting_data':
            return resp;
        else:
            return getGoogleSheets(method,payload,event_id)
    else:
        access_token = account_settings.access_token
        calender_id = 'primary'
        authorization = "Bearer "+access_token
        headers = {
              'Accept': 'application/json',
              'Authorization': authorization,
              'Content-Type': 'application/json'
            }
        conn = http.client.HTTPSConnection("www.googleapis.com")
        try:
            if get_list:
                conn.request('GET',"/calendar/v3/users/me/calendarList/",headers=headers)
            elif method=='POST':
                conn.request("POST", "/calendar/v3/calendars/"+calender_id+"/events?key="+account_settings.key, payload, headers)
            else:
                conn.request(method,"/calendar/v3/calendars/"+calender_id+"/events/"+event_id,payload,headers)
            res = conn.getresponse()
            data = res.read()
            response = json.loads(data.decode("utf-8"))
            return response;  
        except:
            return 'google_calender_api_error';


class GoogleSheetView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # GoogleDriveAuth.objects.filter(status=True).update(status=False)
        account_settings = GoogleDriveAuth.objects.filter(status=True).first()
        if not account_settings:
            
            return HttpResponse('Please ensure Google drive auth is added')


        # payload = "{\"summary\": \""+'My Topic'+"\",\"location\": \""+'MY Location'+"\",\"description\":\""+'description'+"\",\"start\": {\"dateTime\": \""+start.strftime("%Y-%m-%dT%H:%M:%S")+"\",\"timeZone\": \""+timezone+"\"},\"end\": {\"dateTime\": \""+end.strftime("%Y-%m-%dT%H:%M:%S")+"\",\"timeZone\": \""+timezone+"\"},\"attendees\": [{\"email\": \""+default_atendee+"\"}],\"reminders\": {\"useDefault\": \"false\",\"overrides\": [{\"method\": \"email\", \"minutes\": \"10\"},{\"method\": \"popup\", \"minutes\": \"10\"}]}}"
        response_data = getGoogleSheets("POST",'',None)
        if response_data =='error_of_geting_token' or response_data =='error_on_getting_data':
            return HttpResponse('Cannot generate access token automatically.please try some times later.')
        elif response_data == 'google_calender_api_error':
            return HttpResponse('error on google api. Make sure everything correct and stable nertwork')
        else:
            print(response_data)
        return HttpResponse('success')