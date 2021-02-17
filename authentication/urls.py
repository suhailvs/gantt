from django.urls import include, path
from authentication import views
app_name = 'authentication'

urlpatterns = [
	path('', views.Profile.as_view(), name='profile'),
	path('change_password/', views.change_password_view, name='change_password'),
]
