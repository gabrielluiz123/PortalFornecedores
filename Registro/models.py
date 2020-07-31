from django.db import models
from django.utils import timezone
from Cliente.models import Revenda, Cliente_Final, Vendedor, Revenda_User
from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_apphooks_config.managers import AppHookConfigManager
from django.db import models


class Projeto(models.Model):
    aplicacao = models.TextField(verbose_name='Aplicação')
    esp_tec = models.TextField(verbose_name='Especificações Técnicas')
    homologa = models.BooleanField(default=False, verbose_name='Homologado')
    colet_dados = models.TextField(verbose_name='Coletor de dados')
    parc_soft = models.CharField(max_length=255, verbose_name='Parceiro de software')
    date_concl = models.DateField(default=timezone.now, verbose_name='Data de Conclusão')
    info_ad = models.TextField(verbose_name='Informações adicionais')

    objects = AppHookConfigManager()

    def __str__(self):
        return self.aplicacao


class Url(models.Model):
    url = models.CharField(max_length=250,verbose_name='URL')
    empresa = models.CharField(max_length=250,verbose_name='Empresa')

    objects = AppHookConfigManager()

    def __str__(self):
        return self.empresa


class Gerente(models.Model):
    nome = models.CharField(max_length=250,verbose_name='Nome')
    email = models.CharField(max_length=250,verbose_name='E-mail')
    senha = models.CharField(max_length=250, blank=True, null=True, verbose_name='senha')
    url = models.ForeignKey(Url, on_delete=models.DO_NOTHING,verbose_name='URL')

    def __str__(self):
        return self.email


class Registro(models.Model):
    name = models.CharField(default='Registro Oportunidade', max_length=150, verbose_name='name')
    id_revenda = models.ForeignKey(Revenda, on_delete=models.DO_NOTHING, verbose_name='Revenda')
    id_revenda_user = models.ForeignKey(Revenda_User, on_delete=models.DO_NOTHING, verbose_name='Revenda Usuário', blank=True, null=True)
    id_cliente = models.ForeignKey(Cliente_Final, on_delete=models.DO_NOTHING, verbose_name='Cliente Final')
    id_projeto = models.ForeignKey(Projeto, on_delete=models.DO_NOTHING, verbose_name='Projeto')
    vendedor = models.CharField(max_length=255, verbose_name='Vendedor',  blank=True, null=True)
    date_entered = models.DateTimeField(default=timezone.now, verbose_name='Data de entrada')
    contato = models.CharField(max_length=255, verbose_name='Contato Cliente', blank=True, null=True)
    status = models.BooleanField(default=False, verbose_name='Status')
    renovado = models.BooleanField(default=False, verbose_name='Renovado')
    atualizado = models.BooleanField(default=False, verbose_name='Atualizado')
    atualizado_renovado = models.BooleanField(default=False, verbose_name='Atualizado Renovação')
    registro_atualizacao = models.BooleanField(default=False, verbose_name='Registro Atualizado')
    date_atualizado = models.DateField(verbose_name='Data Atualização', blank=True, null=True)
    date_validade = models.DateField(verbose_name='Data Validade', blank=True, null=True)
    data_att_registro = models.DateField(verbose_name='Data Atualização Registro', blank=True, null=True)
    numero_registro = models.CharField(max_length=150, verbose_name='Número de Registro', blank=True, null=True)
    marca = models.CharField(max_length=150, verbose_name='Marca', blank=True, null=True)
    rede = models.CharField(max_length=250, verbose_name='Rede', blank=True, null=True)

    def __str__(self):
        return self.name



