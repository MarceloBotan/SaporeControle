# Generated by Django 4.2 on 2023-04-13 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telecom', '0012_rename_lineplanmodel_lineplan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boxmodel',
            name='date_release',
        ),
        migrations.AlterField(
            model_name='smartmodel',
            name='date_release',
            field=models.DateField(verbose_name='Data de Lançamento'),
        ),
    ]
