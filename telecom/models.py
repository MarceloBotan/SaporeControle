from django.db import models
from django.utils import timezone

LINE_STATUS_CHOICES = [
    ("VERIFICANDO","Verificando",),
    ("SEM CONSUMO","Sem Consumo",),
    ("AGUARDANDO ATIVACAO","Aguard. Ativ.",),
    ("AGUARDANDO ENDERECO","Aguard. Endereço",),
    ("ATIVO","Ativo",),
    ("DISPONIVEL","Disponível",),
    ("ATUALIZADO","Atualizado",),
    ("NAO ATUALIZADO","Não Atualizado",),
    ("BLOQUEADO","Bloqueado",),
    ("CANCELADO","Cancelado",),
    ("VIP","VIP",),
    ("CR ENCERRADO","CR Encerrado",),
]

LINE_PLAN_CHOICES = [
    ("BOX","Box",),
    ("MODEM","Modem",),
    ("SMART","Smart",),
]

LINE_TELECOM_CHOICES = [
    ("CLARO","Claro",),
    ("TIM","TIM",),
    ("VIVO","Vivo",),
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
    ("RETORNOU","Retornou",),
    ("ROUBO","Roubo",),
    ("FURTO","Furto",),
    ("BLOQUEADO","Bloqueado",),
    ("QUEBRADO","Quebrado",),
    ("CR ENCERRADO","CR Encerrado",),
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
    ("RETORNOU","Retornou",),
    ("ROUBO","Roubo",),
    ("FURTO","Furto",),
    ("BLOQUEADO","Bloqueado",),
    ("QUEBRADO","Quebrado",),
    ("CR ENCERRADO","CR Encerrado",),
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
    date_update = models.DateField(default=timezone.now, blank=True)

class Smartphone(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, default='-', verbose_name='IMEI 1')
    imei_2 = models.CharField(max_length=15, default='-', verbose_name='IMEI 2')
    s_model = models.CharField(max_length=31, default='-', choices=SMARTPHONE_MODEL_CHOICES, verbose_name='Modelo')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    status = models.CharField(max_length=31, default='-', choices=SMARTPHONE_STATUS_CHOICES, verbose_name='Status')
    date_update = models.DateField(default=timezone.now, blank=True)

class VivoBox(models.Model):
    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    branch = models.IntegerField(default=0, verbose_name='Filial')
    number = models.BigIntegerField(default=0, verbose_name='Número')
    imei_1 = models.CharField(max_length=15, default='-', verbose_name='IMEI 1')
    v_model = models.CharField(max_length=31, default='-', choices=VIVOBOX_MODEL_CHOICES, verbose_name='Modelo')
    receipt = models.IntegerField(default=0, verbose_name='Nota Fiscal')
    status = models.CharField(max_length=31, default='-', choices=VIVOBOX_STATUS_CHOICES, verbose_name='Status')
    date_update = models.DateField(default=timezone.now, blank=True)

class Branch(models.Model):
    name = models.CharField(max_length=255, default='-')
    branch = models.IntegerField(default=0)
    regional = models.CharField(max_length=3, default='-')
    structure = models.CharField(max_length=31, default='-')
    closed = models.CharField(max_length=1, default='-')
