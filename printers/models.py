from django.db import models
from django.utils import timezone

class Printer(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    serial_number = models.CharField(max_length=255, default='-', verbose_name='Nome')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    auth_attachment = models.FileField(blank=True, upload_to='vivobox_docs/%Y/%m', verbose_name='Autorização')

    tracking_code = models.CharField(max_length=13, default='-', verbose_name='Código de Rastreio')

    def __str__(self) -> str:
        return self.serial_number