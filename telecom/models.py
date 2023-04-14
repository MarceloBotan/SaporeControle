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

LINE_STATUS_RFP_CHOICES = [
    ("ATIVO","Ativo",),
    ("ATIVO FORA RFP","Ativo Fora RFP",),
    ("BLOQUEADO","Bloqueado",),
    ("BLOQUEADO FORA RFP","Bloqueado Fora RFP",),
    ("SUSPENSO","Suspenso",),
    ("SUSPENSO FORA RFP","Suspenso Fora RFP",),
    ("CANCELADO","Cancelado",),
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

LINE_STATUS_CHOICES = [
    ("ATIVO","Ativo",),
    ("BLOQUEADO","Bloqueado",),
    ("CANCELADO","Cancelado",),
    ("DISPONIVEL","Disponível",),
]

SMARTPHONE_STATUS_CHOICES = [
    ("ESTOQUE","Estoque",),
    ("CONFIGURADO","Configurado",),
    ("AGUARDANDO SCI","Aguard. SCI",),
    ("AGUARDANDO TERMO","Aguard. Termo",),
    ("TERMO ASSINADO","Termo Assinado",),
    ("AGUARDANDO ENDERECO","Aguard. End.",),
    ("ENVIADO","Enviado",),
    ("ENTREGUE","Entregue",),
    ("ROUBO","Roubo",),
    ("FURTO","Furto",),
    ("BLOQUEADO","Bloqueado",),
    ("QUEBRADO","Quebrado",),
]

VIVOBOX_STATUS_CHOICES = [
    ("ESTOQUE","Estoque",),
    ("CONFIGURADO","Configurado",),
    ("AGUARDANDO ENDERECO","Aguard. End.",),
    ("ENVIADO","Enviado",),
    ("ENTREGUE","Entregue",),
    ("ROUBO","Roubo",),
    ("FURTO","Furto",),
    ("BLOQUEADO","Bloqueado",),
    ("QUEBRADO","Quebrado",),
]

class Line(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, unique=True, verbose_name='Número')
    sim_card = models.CharField(max_length=20, default='-', verbose_name='SIM Card')
    sim_card_old = models.CharField(max_length=20, default='-')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    plan = models.ForeignKey('LinePlan', on_delete=models.DO_NOTHING)
    telecom = models.CharField(default='-', max_length=15)
    status = models.CharField(max_length=31, default='-', choices=LINE_STATUS_CHOICES, verbose_name='Status')
    status_rfp = models.CharField(max_length=31, default='ATIVO', choices=LINE_STATUS_RFP_CHOICES, \
                                  verbose_name='Status RFP')
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

    def __str__(self):
        return self.name

class LinePlan(models.Model):
    name = models.CharField(max_length=31, unique=True, default='-', verbose_name='Plano')
    plan_type = models.CharField(max_length=15, default='DADOS', choices=LINE_PLAN_TYPES, verbose_name='Tipo')

    def __str__(self):
        return self.name

class Smartphone(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, unique=True, default='-', verbose_name='IMEI 1')
    imei_2 = models.CharField(max_length=15, default='-', verbose_name='IMEI 2')
    s_model = models.ForeignKey('SmartModel', on_delete=models.DO_NOTHING, verbose_name='Modelo')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    status = models.CharField(max_length=31, default='-', choices=SMARTPHONE_STATUS_CHOICES, \
                              verbose_name='Status')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    auth_attachment = models.FileField(blank=True, upload_to='smartphone_docs/%Y/%m', verbose_name='Autorização')

    def __str__(self):
        return self.name

class SmartModel(models.Model):
    name = models.CharField(max_length=31, default='-', verbose_name='Modelo')
    date_release = models.DateField(default=timezone.now, verbose_name='Data de Lançamento')

    def __str__(self):
        return self.name

class VivoBox(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, unique=True, default='-', verbose_name='IMEI 1')
    v_model = models.ForeignKey('BoxModel', on_delete=models.DO_NOTHING, verbose_name='Modelo')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    status = models.CharField(max_length=31, default='-', choices=VIVOBOX_STATUS_CHOICES, verbose_name='Status')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    auth_attachment = models.FileField(blank=True, upload_to='vivobox_docs/%Y/%m', verbose_name='Autorização')

    def __str__(self):
        return self.name

class BoxModel(models.Model):
    name = models.CharField(max_length=31, default='-', verbose_name='Modelo')

    def __str__(self):
        return self.name
