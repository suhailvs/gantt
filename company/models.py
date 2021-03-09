from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    folder_id = models.CharField(max_length=255, blank=True)
    milestone_sheet_id = models.CharField(max_length=255, blank=True)
    task_sheet_id = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.title()
