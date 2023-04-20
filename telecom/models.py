from django.db import models
from django.utils import timezone

LINE_ACCOUNTABLE_CHOICES = [
    ("MAPEADO","Mapeado",),
    ("TG","TG",),
    ("SAPORE","Sapore",),
]

LINE_ACTION_CHOICES = [
    ("OK","Ok",),
    ("CANCELAR APOS FIDELIDADE","Cancelar Após Fidelidade",),
    ("CANCELAR EM MAIO","Cancelar em Maio",),
    ("MAPEAR","Mapear",),
]

LINE_PLAN_TYPES = [
    ("VOZ","Voz",),
    ("DADOS","Dados",),
]

LINE_CONSUMPTION_CHOICES = [
    ("COM CONSUMO","Com Consumo",),
    ("SEM CONSUMO 1 MES","Sem Consumo 1 Mês",),
    ("SEM CONSUMO 2 MESES","Sem Consumo 2 Meses",),
    ("SEM CONSUMO 3 MESES","Sem Consumo 3 Meses",),
    ("SEM CONSUMO 4 MESES","Sem Consumo 4 Meses",),
]

class Line(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, unique=True, verbose_name='Número')
    sim_card = models.CharField(max_length=20, default='-', verbose_name='SIM Card')
    sim_card_old = models.CharField(max_length=20, default='-')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    action = models.CharField(max_length=31, default='OK', choices=LINE_ACTION_CHOICES, verbose_name='Ação')
    consumption = models.CharField(max_length=63, default='COM CONSUMO', choices=LINE_CONSUMPTION_CHOICES, \
                                   verbose_name='Consumo')
    vip = models.BooleanField(default=False, verbose_name='VIP')
    accountable = models.CharField(max_length=63, default='ATIVO', choices=LINE_ACCOUNTABLE_CHOICES, \
                                   verbose_name='Responsável')
    name_mapped = models.BooleanField(default=True, verbose_name='Nome Mapeado')
    branch_mapped = models.BooleanField(default=True, verbose_name='CR Mapeado')
    auth_attachment = models.FileField(blank=True, upload_to='line_docs/%Y/%m', verbose_name='Autorização')

    plan = models.ForeignKey('LinePlan', on_delete=models.DO_NOTHING)
    telecom = models.ForeignKey('LineTelecom', on_delete=models.DO_NOTHING)
    status = models.ForeignKey('LineStatus', on_delete=models.DO_NOTHING)
    status_rfp = models.ForeignKey('LineStatusRFP', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

class LinePlan(models.Model):
    name = models.CharField(max_length=31, unique=True, verbose_name='Plano')
    plan_type = models.CharField(max_length=15, default='DADOS', choices=LINE_PLAN_TYPES, verbose_name='Tipo')

    def __str__(self):
        return self.name

class LineTelecom(models.Model):
    name = models.CharField(max_length=31, unique=True, verbose_name='Operadora')

    def __str__(self):
        return self.name

class LineStatus(models.Model):
    name = models.CharField(max_length=31, unique=True, verbose_name='Status')

    def __str__(self):
        return self.name

class LineStatusRFP(models.Model):
    name = models.CharField(max_length=31, unique=True, verbose_name='Status RFP')

    def __str__(self):
        return self.name

class Smartphone(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, unique=True, default='-', verbose_name='IMEI 1')
    imei_2 = models.CharField(max_length=15, default='-', verbose_name='IMEI 2')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    auth_attachment = models.FileField(blank=True, upload_to='smartphone_docs/%Y/%m', verbose_name='Autorização')

    line_id = models.BigIntegerField(default=0)

    obj_model = models.ForeignKey('SmartModel', on_delete=models.DO_NOTHING, verbose_name='Modelo')
    status = models.ForeignKey('SmartStatus', on_delete=models.DO_NOTHING, verbose_name='Status')

    def __str__(self):
        return self.s_model.name

class SmartModel(models.Model):
    name = models.CharField(max_length=31, verbose_name='Modelo')
    date_release = models.DateField(default=timezone.now, verbose_name='Data de Lançamento')

    def __str__(self):
        return self.name

class SmartStatus(models.Model):
    name = models.CharField(max_length=31, verbose_name='Status')

    def __str__(self):
        return self.name

class VivoBox(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, unique=True, default='-', verbose_name='IMEI 1')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    auth_attachment = models.FileField(blank=True, upload_to='vivobox_docs/%Y/%m', verbose_name='Autorização')

    line_id = models.BigIntegerField(default=0)
    
    obj_model = models.ForeignKey('BoxModel', on_delete=models.DO_NOTHING, verbose_name='Modelo')
    status = models.ForeignKey('BoxStatus', on_delete=models.DO_NOTHING, verbose_name='Status')

    def __str__(self):
        return self.name

class BoxModel(models.Model):
    name = models.CharField(max_length=31, verbose_name='Modelo')

    def __str__(self):
        return self.name

class BoxStatus(models.Model):
    name = models.CharField(max_length=31, verbose_name='Status')

    def __str__(self):
        return self.name
