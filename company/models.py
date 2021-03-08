from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=200, default='Test Company')
    folder_id = models.CharField(max_length=200, blank=True)
    def __str__(self):
        return self.name
