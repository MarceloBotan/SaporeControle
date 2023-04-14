# Generated by Django 4.2 on 2023-04-14 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telecom', '0014_alter_line_number_alter_lineplan_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineplan',
            name='plan_type',
            field=models.CharField(choices=[('VOZ', 'Voz'), ('DADOS', 'Dados')], default='DADOS', max_length=15, verbose_name='Tipo'),
        ),
        migrations.AlterField(
            model_name='line',
            name='status_rfp',
            field=models.CharField(choices=[('ATIVO', 'Ativo'), ('ATIVO FORA RFP', 'Ativo Fora RFP'), ('BLOQUEADO', 'Bloqueado'), ('BLOQUEADO FORA RFP', 'Bloqueado Fora RFP'), ('SUSPENSO', 'Suspenso'), ('SUSPENSO FORA RFP', 'Suspenso Fora RFP'), ('CANCELADO', 'Cancelado')], default='ATIVO', max_length=31, verbose_name='Status RFP'),
        ),
        migrations.AlterField(
            model_name='line',
            name='telecom',
            field=models.CharField(default='-', max_length=15),
        ),
    ]