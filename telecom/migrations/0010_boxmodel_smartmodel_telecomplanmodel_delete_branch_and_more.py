# Generated by Django 4.2 on 2023-04-13 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telecom', '0001_initial_squashed_0009_alter_uploadfile_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoxModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='-', max_length=31, verbose_name='Modelo')),
                ('date_release', models.DateField(blank=True, verbose_name='Data de Lançamento')),
            ],
        ),
        migrations.CreateModel(
            name='SmartModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='-', max_length=31, verbose_name='Modelo')),
                ('date_release', models.DateField(blank=True, verbose_name='Data de Lançamento')),
            ],
        ),
        migrations.CreateModel(
            name='TelecomPlanModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='-', max_length=31, verbose_name='Plano')),
            ],
        ),
        migrations.DeleteModel(
            name='Branch',
        ),
        migrations.DeleteModel(
            name='UploadFile',
        ),
        migrations.AlterField(
            model_name='line',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='telecom.telecomplanmodel'),
        ),
        migrations.AlterField(
            model_name='smartphone',
            name='s_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='telecom.smartmodel'),
        ),
        migrations.AlterField(
            model_name='vivobox',
            name='v_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='telecom.boxmodel'),
        ),
    ]
