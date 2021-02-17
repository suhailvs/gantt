from django.urls import include, path
from projects import views

app_name='projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('add/', views.ProjectCreateView.as_view(), name='project_add'),
    path('gantt/', views.ProjectGanttView.as_view(), name='project_gantt'),
    
]