from django.shortcuts import render, redirect
from django.views import View
from Registro.models import Projeto, Registro, Url, Gerente
from Cliente.models import Vendedor, Revenda, Revenda_User
from Equipamento.models import Equipamento, Equip_Projeto
from Renovacao.models import Renovacao_Registro
import pymysql
from datetime import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
import smtplib
import email.message
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
import requests


@apphook_pool.register
class RenovacaoApphook(CMSApp):
    app_name = "renovacao"  # must match the application namespace
    name = "Renovacao"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["Renovacao.urls"]


class DetalhesIndex(View):
    model = 'Renovacao'
    template_name = 'Renovacao/index.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        print(request.META['HTTP_HOST'])
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa

        self.id_user = request.user
        try:
            self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        except:
            self.vendedor_user = None
        self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
        self.renovacoes_att = Renovacao_Registro.objects.filter(atualizado=False, registro__marca=self.empresa)
        self.registros_att_att = Registro.objects.filter(registro_atualizacao=True, marca=self.empresa, atualizado=True)
        self.count_registro = len(self.registros_att) + len(self.registros_att_att)
        self.count_renovacao = len(self.renovacoes_att)
        if self.vendedor_user:
            self.renovacao = Renovacao_Registro.objects.filter(registro__marca=self.empresa).order_by('-date_created')
        else:
            try:
                self.revenda_user_id = Revenda_User.objects.filter(user_revenda=self.id_user).first()
                if self.revenda_user_id.is_admin:
                    self.revenda = Revenda.objects.filter(revenda_user__user_revenda=self.id_user).first()
                    self.renovacao = Renovacao_Registro.objects.filter(registro__id_revenda=self.revenda, registro__marca=self.empresa).order_by('-date_created')
                    self.renovacao_att = Renovacao_Registro.objects.filter(registro__id_revenda=self.revenda, registro__marca=self.empresa, atualizado=False)
                    self.count_renovacao = len(self.renovacoes_att)

                else:
                    self.renovacao = Renovacao_Registro.objects.filter(registro__id_revenda_user=self.revenda_user_id, registro__marca=self.empresa).order_by('-date_created')
                    self.renovacao_att = Renovacao_Registro.objects.filter(registro__id_revenda_user=self.revenda_user_id, registro__marca=self.empresa, atualizado=False)
                    self.count_renovacao = len(self.renovacoes_att)
            except:
                self.id_vendedor_id = Vendedor.objects.filter(user_vendedor=self.id_user).first()
                self.renovacao = Renovacao_Registro.objects.filter(registro__id_vendedor=self.id_vendedor_id, registro__marca=self.empresa).order_by('-date_created')
        page = request.GET.get('page', 1)
        paginator = Paginator(self.renovacao, 6)
        try:
            self.renovacao = paginator.page(page)
        except PageNotAnInteger:
            self.renovacao = paginator.page(1)
        except EmptyPage:
            self.renovacao = paginator.page(paginator.num_pages)

        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.renovacao,
            'renovacoes': self.renovacao,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class DetalheRenovacao(View):
    template_name = 'Renovacao/detalhe.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.id_user = request.user
        try:
            self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        except:
            self.vendedor_user = None
        try:
            self.revenda_user_id = Revenda_User.objects.get(user_revenda=self.id_user)
        except:
            self.revenda_user_id = None
        if request.user.is_authenticated:
            pk = self.kwargs.get('pk')
            self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
            try:
                if not self.vendedor_user:
                    if self.revenda_user_id.is_admin:
                        self.renovacao = Renovacao_Registro.objects.get(registro__id_revenda=self.revenda_user_id.revenda,
                                                                        pk=pk, registro__marca=self.empresa)
                    else:
                        self.renovacao = Renovacao_Registro.objects.get(registro__id_revenda_user=self.revenda_user_id, pk=pk, registro__marca=self.empresa)
                else:
                    self.renovacao = Renovacao_Registro.objects.get(pk=pk)
                self.id_projeto = self.renovacao.registro.id_projeto
                self.pns = Equip_Projeto.objects.filter(id_projeto=self.id_projeto)
                self.i = self.j = None
                for self.pn in self.pns:
                    if self.pn.id_equip.is_acessorio:
                        self.j = 1
                    else:
                        self.i = 1
            except:
                self.renovacao = None
                self.i = self.j = None
            if request.user.is_authenticated:
                nome = request.user.first_name.strip().split(' ')[0]
            else:
                nome = None
            today = timezone.now()
            self.contexto = {
                'today': today,
                'nome': nome,
                'aprovado': True,
                'empresa': self.empresa,
                'is_gerente': self.vendedor_user,
                'i': self.i,
                'j': self.j,
                'renovacao': self.renovacao,
                'registro': self.renovacao,
                'pnss': self.pns,
                'users': request.user.is_authenticated,
            }
        else:
            redirect('/')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, self.template_name, self.contexto)
        else:
            messages.error(request, 'Logue no sistema para continuar!')
            return redirect('/')

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)

class AprovarRenovacao(DetalhesIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        if self.vendedor_user:
            self.pk = self.kwargs.get('pk')
            self.renovacao_update = Renovacao_Registro.objects.get(pk=self.pk)
            self.registro_update = Renovacao_Registro.objects.get(pk=self.pk).registro
            self.registro_update_cliente = Renovacao_Registro.objects.get(pk=self.pk).registro.id_cliente
            self.renovacao_update.aprovado = True
            self.renovacao_update.atualizado = True
            self.renovacao_update.date_atualizado = timezone.now()

            self.registro_update.date_atualizado = timezone.now()
            self.registro_update.atualizado_renovado = True
            self.registro_update.renovado = True
            self.registro_update.date_validade = timezone.now() + timedelta(days=30)
            try:
                self.registro_update.save()
                self.renovacao_update.save()
                messages.success(request, 'Aprovado com sucesso!!')
            except:
                messages.error(request, 'Falha ao Aprovar.')
            self.url_bd = request.META['HTTP_HOST']
            self.enviaEmail()
            return render(request, self.template_name, self.contexto)
        else:
            return render(request, self.template_name, self.contexto)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def enviaEmail(self):
        me = "gabriel.santos@primeinterway.com.br"
        you = self.registro_update.id_revenda_user.user_revenda.email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Pedido de renovação de Registro Aprovado! Validade: 30 dias."
        msg['From'] = me
        msg['To'] = you
        self.url = f'http://{self.url_bd}/pt/Renovacao/Detalhe/{self.pk}'
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
                            									  <h1 style='margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;'>Pedido de renovação de registro para o cliente {self.registro_update_cliente} foi aprovado! Validade: 30 dias.</h1>
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
                            												  <a href='{self.url}' target='_blank' style='display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;'>Link Para à Renovação</a>
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
                            									  <p style='margin: 0;'>Clique no link acima para ter acesso à Renovação.</p>
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
        msg['To'] = you
        emails = Gerente.objects.filter(url__url=self.url_bd)
        msg["Cc"] = ""
        for email in emails:
            print(email)
            msg["Cc"] = str(email) + "," + msg["Cc"]
        s.sendmail(me, msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
        s.quit()
        return


class ReprovarRenovacao(DetalhesIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        if self.vendedor_user:
            self.pk = self.kwargs.get('pk')
            self.renovacao_update = Renovacao_Registro.objects.get(pk=self.pk)
            self.registro_update = Renovacao_Registro.objects.get(pk=self.pk).registro
            self.registro_update_cliente = Renovacao_Registro.objects.get(pk=self.pk).registro.id_cliente
            self.renovacao_update.atualizado = True
            self.renovacao_update.aprovado = False
            self.renovacao_update.date_atualizado = timezone.now()

            self.registro_update.atualizado_renovado = True
            self.registro_update.renovado = False
            try:
                self.registro_update.save()
                self.renovacao_update.save()
                messages.success(request, 'Reprovado com sucesso!!')
                self.url_bd = request.META['HTTP_HOST']
                self.enviaEmail()
                return render(request, self.template_name, self.contexto)
            except:
                messages.error(request, 'Falha ao Reprovar.')
                return render(request, self.template_name, self.contexto)
        else:
            return render(request, self.template_name, self.contexto)

    def get_queryset(self):
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        qs = super().get_queryset()
        return qs

    def enviaEmail(self):
        me = "gabriel.santos@primeinterway.com.br"
        you = self.registro_update.id_revenda_user.user_revenda.email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Pedido de renovação de Registro não foi Aprovado"
        msg['From'] = me
        msg['To'] = you
        self.url = f'http://{self.url_bd}/pt/Renovacao/Detalhe/{self.pk}'
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
                                    									  <h1 style='margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;'>Pedido de renovação de registro para o cliente {self.registro_update_cliente} não foi aprovado!</h1>
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
                                    												  <a href='{self.url}' target='_blank' style='display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;'>Link Para à Renovação</a>
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
                                    									  <p style='margin: 0;'>Clique no link acima para ter acesso à Renovação.</p>
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
        msg['To'] = you
        msg["Cc"] = ""
        emails = Gerente.objects.filter(url__url=self.url_bd)
        for email in emails:
            print(email)
            msg["Cc"] = str(email) + "," + msg["Cc"]
        s.sendmail(me, msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
        s.quit()
        return


class SaveRenovacao(DetalhesIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.pk = self.kwargs.get('pk')
        self.registro = Registro.objects.get(pk=self.pk)
        next_stage = request.POST.get('next_stage')
        comments = request.POST.get('comments')
        homologa_projeto = request.POST.get("homologa_projeto")
        if homologa_projeto == 'sim':
            homologa_projeto = True
        else:
            homologa_projeto = False
        probability = request.POST.get("porcent")
        closed_date = request.POST.get("closed_date")
        visited_date = request.POST.get("visited_date")
        self.registro.renovado = True
        self.registro.atualizado_renovado = False
        self.renovacao_save = Renovacao_Registro(registro=self.registro, visit_date=visited_date, homologa=homologa_projeto, probabilidade=probability, close_date=closed_date, next_stage=next_stage, comments=comments)
        try:
            self.renovacao_save.save()
            self.registro.save()
            messages.success(request, 'Pedido de Renovação efetuado com sucesso!!')
        except:
            messages.error(request, 'Erro ao efetuar pedido de renovação, contate o administrador do site!')
        return render(request, self.template_name, self.contexto)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs