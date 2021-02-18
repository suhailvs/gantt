from django.urls import include, path
from projects import views, googledrive_view

app_name='projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('add/', views.ProjectCreateView.as_view(), name='project_add'),
    path('gantt/', views.ProjectGanttView.as_view(), name='project_gantt'),
 	path('sheets/', googledrive_view.GoogleSheetView.as_view(), name='google_sheets'),
       
]