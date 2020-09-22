from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages, auth
import pymysql
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils import timezone
from .models import Usuario
from Registro.models import Projeto, Registro, Url, Gerente
from Renovacao.models import Renovacao_Registro
from Equipamento.models import Equipamento, Equip_Projeto
from Cliente.models import Vendedor, Revenda, Cliente_Final, Revenda_User
from django.contrib.auth.models import User
from django.core.validators import validate_email
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cms.models.pluginmodel import CMSPlugin
import requests


@apphook_pool.register
class UsuarioApphook(CMSApp):
    app_name = "usuario"  # must match the application namespace
    name = "Usuario"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["Usuario.urls"]



class GerenciarUsuarios(View):
    model = 'Usuario'
    template_name = 'Usuario/gerenciar.html'
    revendas = Revenda.objects.all()
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        page = request.current_page
        cover = None
        if page:
            cover_image_plugin = CMSPlugin.objects.filter(
                placeholder__page=page,
                placeholder__slot='cover_image',
                plugin_type='FilerImagePlugin',
            ).first()
            if cover_image_plugin:
                cover = cover_image_plugin.get_plugin_instance()[0]
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user.id
        self.revenda_user_aprovado = None
        if self.id_user:
            try:
                self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
            except:
                self.vendedor_user = None
            try:
                self.revenda_user = Revenda_User.objects.get(user_revenda=self.id_user).is_admin
                self.revenda_user_aprovado = Revenda_User.objects.get(user_revenda=self.id_user).aprovado
            except:
                self.revenda_user = None
                self.revenda_user_aprovado = None
            self.renovacao_att = Renovacao_Registro.objects.filter(atualizado=False, registro__marca=self.empresa)
            self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
            self.registros_att_att = Registro.objects.filter(registro_atualizacao=True, marca=self.empresa, atualizado=True)
            self.count_registro = len(self.registros_att) + len(self.registros_att_att)
            self.count_renovacao = len(self.renovacao_att)
        else:
            self.vendedor_user = None
            self.revenda_user = None
            self.registros_att = None
            self.count_registro = None
            self.count_renovacao = None
        self.vendedores = Vendedor.objects.all()
        self.user_revenda = Revenda_User.objects.filter(aprovado=False)
        self.count_user_revenda = len(self.user_revenda)
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now()
        if self.revenda_user:
            self.revenda = Revenda_User.objects.get(user_revenda=self.id_user).revenda
            self.users_revenda = Revenda_User.objects.filter(revenda=self.revenda, aprovado=True, user_revenda__is_active=True).order_by('nome')
        else:
            self.users_revenda = None
        self.contexto = {
            'users_revenda': self.users_revenda,
            'today': today,
            'nome': nome,
            'aprovado': self.revenda_user_aprovado,
            'cover': cover,
            'number_user_revenda': self.count_user_revenda,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'revenda_gerente': self.revenda_user,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

        return redirect('index')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class InativarUsuario(GerenciarUsuarios):
    def setup(self, request, *args, **kwargs):
        page = request.current_page
        cover = None
        if page:
            cover_image_plugin = CMSPlugin.objects.filter(
                placeholder__page=page,
                placeholder__slot='cover_image',
                plugin_type='FilerImagePlugin',
            ).first()
            if cover_image_plugin:
                cover = cover_image_plugin.get_plugin_instance()[0]
        super().setup(request, *args, **kwargs)
        pk = self.kwargs.get('pk')
        user = User.objects.get(pk=pk)
        user.is_active = False
        user.save()
        return redirect('gerenciar_usuarios')

    def get(self, request, *args, **kwargs):
        return redirect('gerenciar_usuarios')




class Perfil(View):
    model = 'Usuario'
    template_name = 'Usuario/perfil.html'
    revendas = Revenda.objects.all()
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):

        page = request.current_page
        cover = None
        if page:
            cover_image_plugin = CMSPlugin.objects.filter(
                placeholder__page=page,
                placeholder__slot='cover_image',
                plugin_type='FilerImagePlugin',
            ).first()
            if cover_image_plugin:
                cover = cover_image_plugin.get_plugin_instance()[0]
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user.id
        self.revenda_user_aprovado = None
        if self.id_user:
            try:
                self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
            except:
                self.vendedor_user = None
            try:
                self.revenda_user = Revenda_User.objects.get(user_revenda=self.id_user).is_admin
                self.revenda_user_aprovado = Revenda_User.objects.get(user_revenda=self.id_user).aprovado
            except:
                self.revenda_user = None
                self.revenda_user_aprovado = None
            self.renovacao_att = Renovacao_Registro.objects.filter(atualizado=False, registro__marca=self.empresa)
            self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
            self.registros_att_att = Registro.objects.filter(registro_atualizacao=True, marca=self.empresa, atualizado=True)
            self.count_registro = len(self.registros_att) + len(self.registros_att_att)
            self.count_renovacao = len(self.renovacao_att)
        else:
            self.vendedor_user = None
            self.revenda_user = None
            self.registros_att = None
            self.count_registro = None
            self.count_renovacao = None
        self.vendedores = Vendedor.objects.all()
        self.user_revenda = Revenda_User.objects.filter(aprovado=False)
        self.count_user_revenda = len(self.user_revenda)
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now()
        self.usuario = request.user
        self.contexto = {
            'usuario': self.usuario,
            'today': today,
            'nome': nome,
            'aprovado': self.revenda_user_aprovado,
            'cover': cover,
            'number_user_revenda': self.count_user_revenda,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'revenda_gerente': self.revenda_user,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

        return redirect('index')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)



class SalvaPerfil(View):
    model = 'Usuario'
    template_name = 'Usuario/perfil.html'
    revendas = Revenda.objects.all()
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        page = request.current_page
        cover = None
        if page:
            cover_image_plugin = CMSPlugin.objects.filter(
                placeholder__page=page,
                placeholder__slot='cover_image',
                plugin_type='FilerImagePlugin',
            ).first()
            if cover_image_plugin:
                cover = cover_image_plugin.get_plugin_instance()[0]
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user.id
        self.revenda_user_aprovado = None
        if self.id_user:
            try:
                self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
            except:
                self.vendedor_user = None
            try:
                self.revenda_user = Revenda_User.objects.get(user_revenda=self.id_user).is_admin
                self.revenda_user_aprovado = Revenda_User.objects.get(user_revenda=self.id_user).aprovado
            except:
                self.revenda_user = None
                self.revenda_user_aprovado = None
            self.renovacao_att = Renovacao_Registro.objects.filter(atualizado=False, registro__marca=self.empresa)
            self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
            self.registros_att_att = Registro.objects.filter(registro_atualizacao=True, marca=self.empresa, atualizado=True)
            self.count_registro = len(self.registros_att) + len(self.registros_att_att)
            self.count_renovacao = len(self.renovacao_att)
        else:
            self.vendedor_user = None
            self.revenda_user = None
            self.registros_att = None
            self.count_registro = None
            self.count_renovacao = None
        self.vendedores = Vendedor.objects.all()
        self.user_revenda = Revenda_User.objects.filter(aprovado=False)
        self.count_user_revenda = len(self.user_revenda)
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now()
        nome_perfil = request.POST.get("nome_perfil")
        self.senha = request.POST.get("pwd_perfil_confirma")
        self.senha2 = request.POST.get("pwd_perfil_confirma_2")
        user = User.objects.get(pk=request.user.id)
        user.first_name = nome_perfil
        user.save()
        self.usuario = request.user
        self.contexto = {
            'usuario': self.usuario,
            'today': today,
            'nome': nome,
            'aprovado': self.revenda_user_aprovado,
            'cover': cover,
            'number_user_revenda': self.count_user_revenda,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'revenda_gerente': self.revenda_user,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

        if self.senha:
            print("SENHA")
            print(len(self.senha))
            if len(self.senha) < 6:
                print("AAAAABB")
                messages.error(request, 'Senha deve ter mais do que 6 caracteres!')
                return render(request, self.template_name, self.contexto)
            elif self.senha != self.senha2:
                messages.error(request, 'Senhas não correspondem!')
                return render(request, self.template_name, self.contexto)
            else:
                user.set_password(self.senha)
                user.save()
        return redirect('index')

    def get(self, request, *args, **kwargs):
        if self.senha:
            print("SENHA")
            print(len(self.senha))
            if len(self.senha) < 6:
                print("AAAAABB")
                messages.error(request, 'Senha deve ter mais do que 6 caracteres!')
                return render(request, self.template_name, self.contexto)
            elif self.senha != self.senha2:
                messages.error(request, 'Senhas não correspondem!')
                return render(request, self.template_name, self.contexto)
        return redirect('index')

    def post(self, request, *args, **kwargs):
        if self.senha:
            print("SENHA")
            print(len(self.senha))
            if len(self.senha) < 6:
                print("AAAAABB")
                messages.error(request, 'Senha deve ter mais do que 6 caracteres!')
                return render(request, self.template_name, self.contexto)
            elif self.senha != self.senha2:
                messages.error(request, 'Senhas não correspondem!')
                return render(request, self.template_name, self.contexto)
        return redirect('index')



class ResetConfirma(View):
    model = 'Usuario'
    template_name = 'Usuario/reset_pwd.html'
    revendas = Revenda.objects.all()
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        page = request.current_page
        cover = None
        if page:
            cover_image_plugin = CMSPlugin.objects.filter(
                placeholder__page=page,
                placeholder__slot='cover_image',
                plugin_type='FilerImagePlugin',
            ).first()
            if cover_image_plugin:
                cover = cover_image_plugin.get_plugin_instance()[0]
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user.id
        self.revenda_user_aprovado = None
        if self.id_user:
            try:
                self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
            except:
                self.vendedor_user = None
            try:
                self.revenda_user = Revenda_User.objects.get(user_revenda=self.id_user).is_admin
                self.revenda_user_aprovado = Revenda_User.objects.get(user_revenda=self.id_user).aprovado
            except:
                self.revenda_user = None
                self.revenda_user_aprovado = None
            self.renovacao_att = Renovacao_Registro.objects.filter(atualizado=False, registro__marca=self.empresa)
            self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
            self.registros_att_att = Registro.objects.filter(registro_atualizacao=True, marca=self.empresa, atualizado=True)
            self.count_registro = len(self.registros_att) + len(self.registros_att_att)
            self.count_renovacao = len(self.renovacao_att)
        else:
            self.vendedor_user = None
            self.revenda_user = None
            self.registros_att = None
            self.count_registro = None
            self.count_renovacao = None
        self.vendedores = Vendedor.objects.all()
        self.user_revenda = Revenda_User.objects.filter(aprovado=False)
        self.count_user_revenda = len(self.user_revenda)
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now()
        self.email_reset = request.POST.get("email_reset_confirma")
        self.contexto = {
            'email_reset': self.email_reset,
            'today': today,
            'nome': nome,
            'aprovado': self.revenda_user_aprovado,
            'cover': cover,
            'number_user_revenda': self.count_user_revenda,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'revenda_gerente': self.revenda_user,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

        return redirect('index')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)

    def post(self, request, *args, **kwargs):
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None

        today = timezone.now()
        self.email_reset = request.POST.get("email_reset_confirma")
        self.pwd_reset_confirma = request.POST.get("pwd_reset_confirma")
        self.pwd_reset_confirma_2 = request.POST.get("pwd_reset_confirma_2")
        self.pwd_reset_codigo = request.POST.get("pwd_reset_codigo")
        self.contexto = {
            'email_reset': self.email_reset,
            'today': today,
            'nome': nome,
            'empresa': self.empresa,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }
        if self.pwd_reset_confirma != self.pwd_reset_confirma_2:
            messages.error(request, 'Senhas não correspondem!')
            return render(request, self.template_name, self.contexto)
        try:
            user_codigo = Usuario.objects.get(user__username=self.email_reset).token
        except:
            user_codigo = None
        if user_codigo != self.pwd_reset_codigo:

            messages.error(request, 'Códigos não correspondem!')

            return render(request, self.template_name, self.contexto)
        user = User.objects.get(username=self.email_reset)
        user.set_password(self.pwd_reset_confirma)
        user.save()

        self.contexto = {
            'email_reset': self.email_reset,
            'today': today,
            'nome': nome,
            'empresa': self.empresa,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

        return redirect('index')

class ResetIndex(View):
    model = 'Usuario'
    template_name = 'Usuario/reset_pwd.html'
    revendas = Revenda.objects.all()
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        page = request.current_page
        cover = None
        if page:
            cover_image_plugin = CMSPlugin.objects.filter(
                placeholder__page=page,
                placeholder__slot='cover_image',
                plugin_type='FilerImagePlugin',
            ).first()
            if cover_image_plugin:
                cover = cover_image_plugin.get_plugin_instance()[0]
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user.id
        self.revenda_user_aprovado = None
        if self.id_user:
            try:
                self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
            except:
                self.vendedor_user = None
            try:
                self.revenda_user = Revenda_User.objects.get(user_revenda=self.id_user).is_admin
                self.revenda_user_aprovado = Revenda_User.objects.get(user_revenda=self.id_user).aprovado
            except:
                self.revenda_user = None
                self.revenda_user_aprovado = None
            self.renovacao_att = Renovacao_Registro.objects.filter(atualizado=False, registro__marca=self.empresa)
            self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
            self.registros_att_att = Registro.objects.filter(registro_atualizacao=True, marca=self.empresa, atualizado=True)
            self.count_registro = len(self.registros_att) + len(self.registros_att_att)
            self.count_renovacao = len(self.renovacao_att)
        else:
            self.vendedor_user = None
            self.revenda_user = None
            self.registros_att = None
            self.count_registro = None
            self.count_renovacao = None
        self.vendedores = Vendedor.objects.all()
        self.user_revenda = Revenda_User.objects.filter(aprovado=False)
        self.count_user_revenda = len(self.user_revenda)
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now()

        self.email_reset = request.POST.get("email_reset")
        self.contexto = {
            'email_reset': self.email_reset,
            'today': today,
            'nome': nome,
            'aprovado': self.revenda_user_aprovado,
            'cover': cover,
            'number_user_revenda': self.count_user_revenda,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'revenda_gerente': self.revenda_user,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }


    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)

    def post(self, request, *args, **kwargs):
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None

        today = timezone.now()
        self.email_reset = request.POST.get("email_reset")
        try:
            user_name = User.objects.get(username=self.email_reset)
        except:
            messages.error(request, 'E-mail não cadastrado!!');
            return redirect('index')
        try:
            self.user_token = Usuario.objects.get(user__username=self.email_reset)
            self.token_gen = self.id_generator()
            self.user_token.token = self.token_gen
            self.user_token.save()
        except:
            user_name = User.objects.get(username=self.email_reset)
            self.token_gen = self.id_generator()
            user = Usuario(token=self.token_gen, user=user_name)
            user.save()
        self.url_bd = request.META['HTTP_HOST']
        self.enviaEmail()
        self.contexto = {
            'email_reset': self.email_reset,
            'today': today,
            'nome': nome,
            'empresa': self.empresa,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

        return render(request, self.template_name, self.contexto)

    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        letras = string.ascii_uppercase

        for turma in range(40, 100):
            codigo = ''.join(random.choice(letras) for _ in range(4))
        return codigo

    def enviaEmail(self):
        me = "gabriel.santos@primeinterway.com.br"
        you = self.email_reset
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Pedido de Alteração da Senha - Portal Oportunidades "+self.empresa
        msg['From'] = me
        msg['To'] = you
        text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
        style = """\
                                                @media screen {
                            		                @font-face {
                            			                font-family: 'Source Sans Pro';
                            			                font-style: normal;
                            			                font-weight: 400;
                            							  src: local('Source Sans Pro Regular'), local('SourceSansPro-Regular'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff) format('woff');
                            						}

                            						@font-face {
                            							font-family: 'Source Sans Pro';
                            							font-style: normal;
                            							  font-weight: 700;
                            							  src: local('Source Sans Pro Bold'), local('SourceSansPro-Bold'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff) format('woff');
                            							}
                            						  }

                            						  body,
                            						  table,
                            						  td,
                            						  a {
                            							-ms-text-size-adjust: 100%; 
                            							-webkit-text-size-adjust: 100%; 
                            						  }
                            						  table,
                            						  td {
                            							mso-table-rspace: 0pt;
                            							mso-table-lspace: 0pt;
                            						  }
                            						  img {
                            							-ms-interpolation-mode: bicubic;
                            						  }
                            						  a[x-apple-data-detectors] {
                            							font-family: inherit !important;
                            							font-size: inherit !important;
                            							font-weight: inherit !important;
                            							line-height: inherit !important;
                            							color: inherit !important;
                            							text-decoration: none !important;
                            						  }
                            						  div[style*='margin: 16px 0;'] {
                            							margin: 0 !important;
                            						  }

                            						  body {
                            							width: 100% !important;
                            							height: 100% !important;
                            							padding: 0 !important;
                            							margin: 0 !important;
                            						  }
                            						  table {
                            							border-collapse: collapse !important;
                            						  }

                            						  a {
                            							color: #1a82e2;
                            						  }

                            						  img {
                            							height: auto;
                            							line-height: 100%;
                            							text-decoration: none;
                            							border: 0;
                            							outline: none;
                            						  }
                            						  """

        html = f"""\
                                    <html>
                            			<head>

                            				<meta charset='utf-8'>
                            						  <meta http-equiv='x-ua-compatible' content='ie=edge'>
                            						  <title>Password Reset</title>
                            						  <meta name='viewport' content='width=device-width, initial-scale=1'>
                            						  <style type='text/css'>
                                                        {style}
                             </style>

                            						</head>
                            						<body style='background-color: #e9ecef;'>
                            						  <div class='preheader' style='display: none; max-width: 0; max-height: 0; overflow: hidden; font-size: 1px; line-height: 1px; color: #fff; opacity: 0;'>
                            							A preheader is the short summary text that follows the subject line when an email is viewed in the inbox.
                            						  </div>
                            						  <table border='0' cellpadding='0' cellspacing='0' width='100%'>
                            							<tr>
                            							  <td align='center' bgcolor='#e9ecef'>
                            								<table border='0' cellpadding='0' cellspacing='0' width='100%' style='max-width: 600px;'>
                            								  <tr>
                            									<td align='center' valign='top' style='padding: 20px 24px;'>

                            										<img src='https://crmprime.grupo-artico.com/custom/themes/default/images/{self.empresa}.png' alt='Logo' border='0' style='display: block; '>
                            									  </a>
                            									</td>
                            								  </tr>
                            								</table>
                            							  </td>
                            							</tr>
                            							<tr>
                            							  <td align='center' bgcolor='#e9ecef'>
                            								<table border='0' cellpadding='0' cellspacing='0' width='100%' style='max-width: 600px;'>
                            								  <tr>
                            									<td align='center' bgcolor='#ffffff' style='padding: 36px 24px 0; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; border-top: 3px solid #d4dadf;'>
                            									  <h1 style='margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;'>Foi solicitado a troca de senha para este e-mail!</h1>
                            									</td>
                            								  </tr>
                            								</table>
                            							  </td>
                            							</tr>
                            							<tr>
                            							  <td align='center' bgcolor='#e9ecef'>
                            								<table border='0' cellpadding='0' cellspacing='0' width='100%' style='max-width: 600px;'>
                            								  <tr>
                            									<td align='left' bgcolor='#ffffff'>
                            									  <table border='0' cellpadding='0' cellspacing='0' width='100%'>
                            										<tr>
                            										  <td align='center' bgcolor='#ffffff' style='padding: 12px;'>
                            											<table border='0' cellpadding='0' cellspacing='0'>
                            											  <tr>
                            												<td align='center' bgcolor='#bcdbf7' style='border-radius: 6px;'>
                            												  <p>Segue Código para efetuar a Troca: {self.token_gen}</p>
                            												</td>
                            											  </tr>
                            											</table>
                            										  </td>
                            										</tr>
                            									  </table>
                            									</td>
                            								  </tr>
                            								</table>
                            							  </td>
                            							</tr>
                            							<tr>
                            							  <td align='center' bgcolor='#e9ecef' style='padding: 24px;'>
                            								<table border='0' cellpadding='0' cellspacing='0' width='100%' style='max-width: 600px;'>
                            								  <tr>
                            									<td align='center' bgcolor='#e9ecef' style='padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;'>
                        
                            									</td>
                            								  </tr>

                            								</table>
                            							  </td>
                            							</tr>

                            						  </table>

                            						</body>
                            						</html>
                                    """
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        emails = Gerente.objects.get(url__url=self.url_bd, nome='noreply')
        me = emails.email
        s.login(me, emails.senha)
        msg['To'] = you+', gabriel.santos@primeinterway.com.br'
        s.sendmail(me, you, msg.as_string())
        s.quit()
        return