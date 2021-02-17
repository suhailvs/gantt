from django.db import models
from django.conf import settings

# Create your models here.

class Project(models.Model):    
    project_id = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    start_date= models.DateTimeField()
    end_date = models.DateTimeField()
    progress = models.IntegerField(default=0)
    dependencies = models.CharField(max_length=50, blank=True) # project id dependences
    created_on = models.DateTimeField(auto_now_add = True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
