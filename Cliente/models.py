from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Revenda(models.Model):
    razao_social = models.CharField(max_length=255, verbose_name='Razão Social')
    cnpj = models.CharField(max_length=255, verbose_name='CNPJ')
    rua = models.CharField(max_length=255, verbose_name='Rua')
    cidade = models.CharField(max_length=255, verbose_name='Cidade')
    estado = models.CharField(max_length=255, verbose_name='Estado')
    contato = models.CharField(max_length=255, verbose_name='Contato')
    cep = models.CharField(default=12120000, max_length=255, verbose_name='Cep')
    telefone = models.CharField(max_length=255, verbose_name='Telefone')
    date_entered = models.DateTimeField(default=timezone.now, verbose_name='Data de entrada')

    def __str__(self):
        return self.razao_social


class Cliente_Final(models.Model):
    razao_social = models.CharField(max_length=255, verbose_name='Razão Social')
    cnpj = models.CharField(max_length=255, verbose_name='CNPJ')
    rua = models.CharField(max_length=255, verbose_name='Rua')
    cidade = models.CharField(max_length=255, verbose_name='Cidade')
    estado = models.CharField(max_length=255, verbose_name='Estado')
    cep = models.CharField(default=12120000, max_length=255, verbose_name='CEP')
    telefone = models.CharField(max_length=255, verbose_name='Telefone')
    email = models.CharField(max_length=255, verbose_name='E-mail', blank=True, null=True)
    rede = models.CharField(max_length=255, verbose_name='Rede', blank=True, null=True)
    date_entered = models.DateTimeField(default=timezone.now, verbose_name='Data de entrada')

    def __str__(self):
        return self.razao_social


class Empresa(models.Model):
    nome = models.CharField(max_length=150, verbose_name='Empresa')

    def __str__(self):
        return self.nome


class Vendedor(models.Model):
    nome = models.CharField(max_length=150, verbose_name='Nome')
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, verbose_name='Empresa')
    is_gerente = models.BooleanField(default=False, verbose_name='Gerente de Marca')
    user_vendedor = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuário')

    def __str__(self):
        return self.nome


class Revenda_User(models.Model):
    nome = models.CharField(max_length=150, verbose_name='Nome')
    revenda = models.ForeignKey(Revenda, on_delete=models.DO_NOTHING, verbose_name='Revenda')
    is_admin = models.BooleanField(default=False, verbose_name='Administrador')
    user_revenda = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuário')
    aprovado = models.BooleanField(default=False, verbose_name='Aprovado')

    def __str__(self):
        return self.nome
