# Generated by Django 2.2.3 on 2020-07-10 13:47

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Renovacao', '0004_auto_20200624_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renovacao_registro',
            name='date_created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 7, 10, 13, 47, 30, 209146, tzinfo=utc), null=True, verbose_name='Data de criação'),
        ),
    ]
