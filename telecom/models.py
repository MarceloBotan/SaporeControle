from django.db import models
from django.utils import timezone

LINE_STATUS_CHOICES = [
    ("ATIVO","Ativo",),
    ("BLOQUEADO","Bloqueado",),
    ("CANCELADO","Cancelado",),
    ("DISPONIVEL","Disponível",),
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

LINE_ACCOUNTABLE_CHOICES = [
    ("MAPEADO","Mapeado",),
    ("TG","TG",),
    ("SAPORE","Sapore",),
]

LINE_PLAN_CHOICES = [
    ("CLARO MAX 2.0","Claro Max 2.0",),
    ("CLARO ILIMITADO 2GB","Claro Ilimitado 2GB",),
    ("CLARO ILIMITADO 20GB","Claro Ilimitado 20GB",),
    ("TIM DADOS 3GB","TIM Dados 3GB",),
    ("TIM DADOS 6GB","TIM Dados 6GB",),
    ("VIVO MOVEL 120MB","Vivo Móvel 120MB",),
    ("VIVO BOX 5GB","Vivo Box 5GB",),
    ("VIVO BOX 10GB","Vivo Box 10GB",),
    ("VIVO SMART 0,5GB","Vivo Smart 0,5GB",),
    ("VIVO SMART 2GB","Vivo Smart 2GB",),
    ("VIVO SMART 5GB","Vivo Smart 5GB",),
    ("VIVO SMART 7GB","Vivo Smart 7GB",),
    ("VIVO SMART 25GB","Vivo Smart 25GB",),
]

LINE_PLAN_TYPES = {
    "CLARO MAX 2.0": "VOZ",
    "CLARO ILIMITADO 2GB": "DADOS",
    "CLARO ILIMITADO 20GB": "DADOS",
    "TIM DADOS 3GB": "VOZ",
    "TIM DADOS 6GB": "VOZ",
    "VIVO MOVEL 120MB": "DADOS",
    "VIVO BOX 5GB": "DADOS",
    "VIVO BOX 10GB": "DADOS",
    "VIVO SMART 0,5GB": "VOZ",
    "VIVO SMART 2GB": "VOZ",
    "VIVO SMART 5GB": "VOZ",
    "VIVO SMART 7GB": "VOZ",
    "VIVO SMART 25GB": "VOZ",
}

LINE_TELECOM_CHOICES = [
    ("CLARO","Claro",),
    ("TIM","TIM",),
    ("VIVO","Vivo",),
]

LINE_CONSUMPTION_CHOICES = [
    ("COM CONSUMO","Com Consumo",),
    ("SEM CONSUMO 1 MES","Sem Consumo 1 Mês",),
    ("SEM CONSUMO 2 MESES","Sem Consumo 2 Meses",),
    ("SEM CONSUMO 3 MESES","Sem Consumo 3 Meses",),
    ("SEM CONSUMO 4 MESES","Sem Consumo 4 Meses",),
]

LINE_ACTION_CHOICES = [
    ("OK","Ok",),
    ("CANCELAR APOS FIDELIDADE","Cancelar Após Fidelidade",),
    ("CANCELAR EM MAIO","Cancelar em Maio",),
    ("MAPEAR","Mapear",),
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

SMARTPHONE_MODEL_CHOICES = [
    ("LG K130F","LG K130F",),
    ("MOTO E4","Moto E4",),
    ("MOTO G4 Play","Moto G4 Play",),
    ("MOTO G5S","Moto G5S",),
    ("MOTO G8 Power Lite","Moto G8 Power Lite",),
    ("MOTO G20","Moto G20",),
    ("MOTO G22","Moto G22",),
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

VIVOBOX_MODEL_CHOICES = [
    ("HUAWEI-E173","Huawei-E173",),
    ("MF253M","MF253M",),
    ("WLD71-T5","WLD71-T5",),
    ("BC-4GMCPGa","BC-4GMCPGa",),
]

class Line(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    sim_card = models.CharField(max_length=20, default='-', verbose_name='SIM Card')
    sim_card_old = models.CharField(max_length=20, default='-')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    plan = models.CharField(default='-', max_length=31, choices=LINE_PLAN_CHOICES, verbose_name='Plano')
    telecom = models.CharField(default='-', max_length=15, choices=LINE_TELECOM_CHOICES, verbose_name='Operadora')
    status = models.CharField(max_length=31, default='-', choices=LINE_STATUS_CHOICES, verbose_name='Status')
    status_rfp = models.CharField(max_length=31, default='-', choices=LINE_STATUS_RFP_CHOICES, \
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

class Smartphone(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, default='-', verbose_name='IMEI 1')
    imei_2 = models.CharField(max_length=15, default='-', verbose_name='IMEI 2')
    s_model = models.CharField(max_length=31, default='-', choices=SMARTPHONE_MODEL_CHOICES, \
                               verbose_name='Modelo')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    status = models.CharField(max_length=31, default='-', choices=SMARTPHONE_STATUS_CHOICES, \
                              verbose_name='Status')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    auth_attachment = models.FileField(blank=True, upload_to='smartphone_docs/%Y/%m', verbose_name='Autorização')

class VivoBox(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, default='-', verbose_name='IMEI 1')
    v_model = models.CharField(max_length=31, default='-', choices=VIVOBOX_MODEL_CHOICES, verbose_name='Modelo')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    status = models.CharField(max_length=31, default='-', choices=VIVOBOX_STATUS_CHOICES, verbose_name='Status')
    date_update = models.DateField(default=timezone.now, blank=True)
    branch_closed = models.BooleanField(default=False)
    auth_attachment = models.FileField(blank=True, upload_to='vivobox_docs/%Y/%m', verbose_name='Autorização')

class Branch(models.Model):
    branch = models.IntegerField(default=0)
    name = models.CharField(max_length=255, default='-')
    structure = models.CharField(max_length=31, default='-')
    closed = models.BooleanField(default=False)
    regional = models.CharField(max_length=3, default='-')

class UploadFile(models.Model):
    file = models.FileField(blank=True, upload_to='', verbose_name='Planilha')