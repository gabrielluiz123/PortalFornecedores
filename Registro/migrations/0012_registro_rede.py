# Generated by Django 2.2.3 on 2020-07-20 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registro', '0011_gerente'),
    ]

    operations = [
        migrations.AddField(
            model_name='registro',
            name='rede',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Rede'),
        ),
    ]
