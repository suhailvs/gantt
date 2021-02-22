from django.urls import include, path
from googleoauth import views

app_name='googleoauth'

urlpatterns = [
    path('', views.CredentialsListView.as_view(), name='credential_list'),    
    # path('credential_update/<int:pk>/', views.CredentialsUpdateView.as_view(), name='credential_update'),
    path('credential_add/', views.CredentialsCreateView.as_view(), name='credential_add'),

    path('login/', views.GoogleAuthView.as_view(), name='login'),
    path('get_files/', views.GetFilesView.as_view(), name='get_files'),
    path('view_spreadsheet/', views.SpreadSheetView.as_view(), name='view_spreadsheet'),
]