from django.urls import include, path
from company import views

app_name='company'

urlpatterns = [
    path('', views.GetFilesView.as_view(), name='get_files'),
    path('chart/', views.GoogleChartView.as_view(), name='chart'),
]