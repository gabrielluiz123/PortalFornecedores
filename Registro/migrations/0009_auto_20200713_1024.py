# Generated by Django 2.2.3 on 2020-07-13 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registro', '0008_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registro',
            name='id_vendedor',
        ),
        migrations.AddField(
            model_name='registro',
            name='vendedor',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Vendedor'),
        ),
    ]