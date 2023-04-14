from django.db import models
from django.utils import timezone

class Branch(models.Model):
    branch = models.IntegerField(default=0, unique=True)
    name = models.CharField(max_length=255, default='-')
    structure = models.CharField(max_length=31, default='-')
    closed = models.BooleanField(default=False)
    regional = models.CharField(max_length=3, default='-')

class UploadFile(models.Model):
    file = models.FileField(blank=True, upload_to='', verbose_name='Planilha')
    date_update = models.DateField(default=timezone.now, blank=True)
