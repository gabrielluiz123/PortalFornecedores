# Generated by Django 2.2.3 on 2020-06-09 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cliente', '0011_revenda_user_aprovado'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente_final',
            name='rede',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Rede'),
        ),
    ]
