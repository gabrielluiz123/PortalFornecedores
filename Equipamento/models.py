from django.db import models
from django.utils import timezone
from Registro.models import Projeto


class Equipamento(models.Model):
    pn = models.CharField(max_length=150, verbose_name='Part Number')
    descricao = models.TextField(verbose_name='Descrição')
    is_acessorio = models.BooleanField(default=False, verbose_name="Acessório")
    is_concorrente = models.BooleanField(default=False, verbose_name="Concorrente")
    date_entered = models.DateTimeField(default=timezone.now, verbose_name='Data de Entrada')

    def __str__(self):
        return self.pn


class Equip_Projeto(models.Model):
    name = models.CharField(max_length=150, default='Equip')
    id_projeto = models.ForeignKey(Projeto, on_delete=models.DO_NOTHING, verbose_name='Projeto')
    id_equip = models.ForeignKey(Equipamento, on_delete=models.DO_NOTHING, verbose_name='Equipamento')
    aprovado = models.BooleanField(default=False, verbose_name='Aprovado')
    atualizado = models.BooleanField(default=False, verbose_name='Atualiazdo')
    valor = models.FloatField(verbose_name='Valor')
    qty = models.IntegerField(default=1,verbose_name='Quantidade')
    number = models.IntegerField(default=0, verbose_name='Number')

    def __str__(self):
        return self.name