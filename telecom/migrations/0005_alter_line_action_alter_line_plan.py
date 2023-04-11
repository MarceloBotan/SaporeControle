# Generated by Django 4.2 on 2023-04-11 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telecom', '0004_alter_line_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='line',
            name='action',
            field=models.CharField(choices=[('OK', 'Ok'), ('CANCELAR APOS FIDELIDADE', 'Cancelar Após Fidelidade'), ('CANCELAR EM MAIO', 'Cancelar em Maio'), ('MAPEAR', 'Mapear')], default='OK', max_length=31, verbose_name='Ação'),
        ),
        migrations.AlterField(
            model_name='line',
            name='plan',
            field=models.CharField(choices=[('CLARO MAX 2.0', 'Claro Max 2.0'), ('CLARO ILIMITADO 2GB', 'Claro Ilimitado 2GB'), ('CLARO ILIMITADO 20GB', 'Claro Ilimitado 20GB'), ('TIM DADOS 3GB', 'TIM Dados 3GB'), ('TIM DADOS 6GB', 'TIM Dados 6GB'), ('VIVO MOVEL 120MB', 'Vivo Móvel 120MB'), ('VIVO BOX 5GB', 'Vivo Box 5GB'), ('VIVO BOX 10GB', 'Vivo Box 10GB'), ('VIVO SMART 0,5GB', 'Vivo Smart 0,5GB'), ('VIVO SMART 2GB', 'Vivo Smart 2GB'), ('VIVO SMART 5GB', 'Vivo Smart 5GB'), ('VIVO SMART 7GB', 'Vivo Smart 7GB'), ('VIVO SMART 25GB', 'Vivo Smart 25GB')], default='-', max_length=31, verbose_name='Plano'),
        ),
    ]
