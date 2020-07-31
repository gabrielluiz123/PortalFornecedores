from django.db import models
from django.utils import timezone
from Cliente.models import Revenda, Cliente_Final, Vendedor, Revenda_User
from django.contrib.auth.models import User
from django.db import models


class Usuario(models.Model):
    token = models.CharField(max_length=255, verbose_name='Aplicação')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Usuário')

    def __str__(self):
        return self.token
