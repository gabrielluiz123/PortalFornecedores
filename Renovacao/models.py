from django.db import models
from Registro.models import Registro
from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_apphooks_config.managers import AppHookConfigManager
from django.utils import timezone

class Renovacao_Registro(models.Model):
    name = models.CharField(default='Renovacao', max_length=150, verbose_name='name')
    registro = models.ForeignKey(Registro, on_delete=models.DO_NOTHING, verbose_name='Registro')
    visit_date = models.DateTimeField(verbose_name='Data ultima visita', blank=True, null=True)
    date_atualizado = models.DateTimeField(verbose_name='Data Atualizacao', blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now(), verbose_name='Data de criação', blank=True, null=True)
    homologa = models.BooleanField(default=False, verbose_name='Homologado')
    probabilidade = models.CharField(default='30%', max_length=150, verbose_name='Probabilidade de fechamento')
    close_date = models.DateTimeField(verbose_name='Data de fechamento', blank=True, null=True)
    next_stage = models.TextField(verbose_name='Proxima Etapa')
    comments = models.TextField(verbose_name='Comentarios')
    aprovado = models.BooleanField(default=False, verbose_name='Aprovado')
    atualizado = models.BooleanField(default=False, verbose_name='Atualizado')

    objects = AppHookConfigManager()

    def __str__(self):
        return self.name