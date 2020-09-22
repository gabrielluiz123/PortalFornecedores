from django.shortcuts import render, redirect
from django.views import View
from Registro.models import Projeto, Registro, Url, Gerente
from Cliente.models import Vendedor, Revenda, Revenda_User
from Equipamento.models import Equipamento, Equip_Projeto
from Renovacao.models import Renovacao_Registro
from datetime import *
import pymysql
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class DetalheApphook(CMSApp):
    app_name = "detalhe"  # must match the application namespace
    name = "Detalhes"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["Detalhes.urls"]


class DetalhesIndex(View):
    model = 'Registro'
    template_name = 'Detalhes/index.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
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
            self.registro = Registro.objects.filter(marca=self.empresa).order_by('-date_entered')
        else:
            try:
                self.revenda_user_id = Revenda_User.objects.filter(user_revenda=self.id_user).first()
                if self.revenda_user_id.is_admin:
                    self.revenda = Revenda.objects.filter(revenda_user__user_revenda=self.id_user).first()
                    self.registro = Registro.objects.filter(id_revenda=self.revenda, marca=self.empresa).order_by(
                        '-date_entered')
                else:
                    self.registro = Registro.objects.filter(id_revenda_user=self.revenda_user_id,
                                                            marca=self.empresa).order_by('-date_entered')
            except:
                self.id_vendedor_id = Vendedor.objects.filter(user_vendedor=self.id_user).first()
                self.registro = Registro.objects.filter(id_vendedor=self.id_vendedor_id, marca=self.empresa).order_by(
                    '-date_entered')
        page = request.GET.get('page', 1)
        paginator = Paginator(self.registro, 6)
        try:
            self.registro = paginator.page(page)
        except PageNotAnInteger:
            self.registro = paginator.page(1)
        except EmptyPage:
            self.registro = paginator.page(paginator.num_pages)

        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        print("AQUI")

        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.registro,
            'registros': self.registro,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }
        print(self.contexto)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class DetalhesIndexExpirado(View):
    model = 'Registro'
    template_name = 'Detalhes/index.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user
        try:
            self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        except:
            self.vendedor_user = None
        self.time = timezone.now()
        self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
        self.renovacoes_att = Renovacao_Registro.objects.filter(atualizado=False, registro__marca=self.empresa)
        self.registros_att_att = Registro.objects.filter(registro_atualizacao=True, marca=self.empresa, atualizado=True)
        self.count_registro = len(self.registros_att) + len(self.registros_att_att)
        self.count_renovacao = len(self.renovacoes_att)
        if self.vendedor_user:
            self.registro = Registro.objects.filter(marca=self.empresa, date_validade__lte=self.time.date(), date_validade__isnull=False).order_by('-date_entered')
        else:
            try:
                self.revenda_user_id = Revenda_User.objects.filter(user_revenda=self.id_user).first()
                if self.revenda_user_id.is_admin:
                    self.revenda = Revenda.objects.filter(revenda_user__user_revenda=self.id_user).first()
                    self.registro = Registro.objects.filter(id_revenda=self.revenda, marca=self.empresa, date_validade__lte=self.time.date(), date_validade__isnull=False).order_by(
                        '-date_entered')
                else:
                    self.registro = Registro.objects.filter(id_revenda_user=self.revenda_user_id,
                                                            marca=self.empresa, date_validade__lte=self.time.date(), date_validade__isnull=False).order_by('-date_entered')
            except:
                self.id_vendedor_id = Vendedor.objects.filter(user_vendedor=self.id_user).first()
                self.registro = Registro.objects.filter(id_vendedor=self.id_vendedor_id, marca=self.empresa, date_validade__lte=self.time.date()).order_by(
                    '-date_entered').exclude(date_validade=False)
        page = request.GET.get('page', 1)
        paginator = Paginator(self.registro, 6)
        try:
            self.registro = paginator.page(page)
        except PageNotAnInteger:
            self.registro = paginator.page(1)
        except EmptyPage:
            self.registro = paginator.page(paginator.num_pages)

        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0].strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.registro,
            'registros': self.registro,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class DetalhesIndexAguardando(View):
    model = 'Registro'
    template_name = 'Detalhes/index.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
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
            self.registro = Registro.objects.filter(marca=self.empresa, atualizado=False).order_by('-date_entered')
        else:
            try:
                self.revenda_user_id = Revenda_User.objects.filter(user_revenda=self.id_user).first()
                if self.revenda_user_id.is_admin:
                    self.revenda = Revenda.objects.filter(revenda_user__user_revenda=self.id_user).first()
                    self.registro = Registro.objects.filter(id_revenda=self.revenda, marca=self.empresa, atualizado=False).order_by(
                        '-date_entered')
                else:
                    self.registro = Registro.objects.filter(id_revenda_user=self.revenda_user_id,
                                                            marca=self.empresa, atualizado=False).order_by('-date_entered')
            except:
                self.id_vendedor_id = Vendedor.objects.filter(user_vendedor=self.id_user).first()
                self.registro = Registro.objects.filter(id_vendedor=self.id_vendedor_id, marca=self.empresa, atualizado=False).order_by(
                    '-date_entered')
        page = request.GET.get('page', 1)
        paginator = Paginator(self.registro, 6)
        try:
            self.registro = paginator.page(page)
        except PageNotAnInteger:
            self.registro = paginator.page(1)
        except EmptyPage:
            self.registro = paginator.page(paginator.num_pages)

        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0].strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.registro,
            'registros': self.registro,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class DetalhesIndexAprovados(View):
    model = 'Registro'
    template_name = 'Detalhes/index.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
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
            self.registro = Registro.objects.filter(marca=self.empresa, atualizado=True, status=True).order_by('-date_entered')
        else:
            try:
                self.revenda_user_id = Revenda_User.objects.filter(user_revenda=self.id_user).first()
                if self.revenda_user_id.is_admin:
                    self.revenda = Revenda.objects.filter(revenda_user__user_revenda=self.id_user).first()
                    self.registro = Registro.objects.filter(id_revenda=self.revenda, marca=self.empresa, atualizado=True, status=True).order_by(
                        '-date_entered')
                else:
                    self.registro = Registro.objects.filter(id_revenda_user=self.revenda_user_id,
                                                            marca=self.empresa, atualizado=True, status=True).order_by('-date_entered')
            except:
                self.id_vendedor_id = Vendedor.objects.filter(user_vendedor=self.id_user).first()
                self.registro = Registro.objects.filter(id_vendedor=self.id_vendedor_id, marca=self.empresa, atualizado=True, status=True).order_by(
                    '-date_entered')
        page = request.GET.get('page', 1)
        paginator = Paginator(self.registro, 6)
        try:
            self.registro = paginator.page(page)
        except PageNotAnInteger:
            self.registro = paginator.page(1)
        except EmptyPage:
            self.registro = paginator.page(paginator.num_pages)

        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.registro,
            'registros': self.registro,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class DetalhesIndexReprovados(View):
    model = 'Registro'
    template_name = 'Detalhes/index.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
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
            self.registro = Registro.objects.filter(marca=self.empresa, atualizado=True, status=False).order_by('-date_entered')
        else:
            try:
                self.revenda_user_id = Revenda_User.objects.filter(user_revenda=self.id_user).first()
                if self.revenda_user_id.is_admin:
                    self.revenda = Revenda.objects.filter(revenda_user__user_revenda=self.id_user).first()
                    self.registro = Registro.objects.filter(id_revenda=self.revenda, marca=self.empresa, atualizado=True, status=False).order_by(
                        '-date_entered')
                else:
                    self.registro = Registro.objects.filter(id_revenda_user=self.revenda_user_id,
                                                            marca=self.empresa, atualizado=True, status=False).order_by('-date_entered')
            except:
                self.id_vendedor_id = Vendedor.objects.filter(user_vendedor=self.id_user).first()
                self.registro = Registro.objects.filter(id_vendedor=self.id_vendedor_id, marca=self.empresa, atualizado=True, status=False).order_by(
                    '-date_entered')
        page = request.GET.get('page', 1)
        paginator = Paginator(self.registro, 6)
        try:
            self.registro = paginator.page(page)
        except PageNotAnInteger:
            self.registro = paginator.page(1)
        except EmptyPage:
            self.registro = paginator.page(paginator.num_pages)

        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'number_renovacao': self.count_renovacao,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.registro,
            'registros': self.registro,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)



class AtualizarRegistro(View):
    model = 'Registro'
    template_name = 'Detalhes/atualizar_registro.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user
        try:
            self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        except:
            self.vendedor_user = None
        pk = self.kwargs.get('pk')
        self.revenda_user = Revenda_User.objects.get(user_revenda=self.id_user).is_admin
        self.revenda_user_u = Revenda_User.objects.get(user_revenda=self.id_user)
        self.revenda = Revenda_User.objects.get(user_revenda=self.id_user).revenda
        if self.revenda_user:
            self.registro_c = Registro.objects.filter(id_revenda=self.revenda)
            self.registro = Registro.objects.get(pk=pk, id_revenda=self.revenda)
        else:
            self.registro_c = Registro.objects.filter(id_revenda=self.revenda, id_revenda_user=self.revenda_user_u)
            self.registro = Registro.objects.get(pk=pk, id_revenda=self.revenda, id_revenda_user=self.revenda_user_u)
        self.count_registro = len(self.registro_c)
        self.id_projeto = self.registro.id_projeto
        self.pns = Equip_Projeto.objects.filter(id_projeto=self.id_projeto)
        self.count_acessorio = 0
        self.count_equip = 0
        self.i = self.j = None
        for self.pn in self.pns:
            if self.pn.id_equip.is_acessorio:
                self.j = 1
                self.count_acessorio = self.count_acessorio + 1
            else:
                self.i = 1
                self.count_equip = self.count_equip + 1
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'equip_number': self.count_equip,
            'acessorio_number': self.count_acessorio,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'registro': self.registro,
            'pnss': self.pns,
            'user': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class AtualizarRegistroSave(DetalhesIndex):
    model = 'Registro'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user
        try:
            self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        except:
            self.vendedor_user = None
        pk = self.kwargs.get('pk')
        self.registro_proj = Registro.objects.get(pk=pk).id_projeto
        self.registro_proj_r = Registro.objects.get(pk=pk)
        self.equip_count = Equip_Projeto.objects.filter(id_projeto=self.registro_proj)
        self.equip_number = 0
        self.acessorio_number = 0
        for pn in self.equip_count:
            if not pn.id_equip.is_acessorio:
                self.equip_number = self.equip_number + 1
            else:
                self.acessorio_number = self.acessorio_number + 1
        for i in range(self.equip_number, 10000):
            if request.POST.get(f'pn_projeto{i}'):
                pn = request.POST.get(f'pn_projeto{i}')
                descr = request.POST.get(f'desc_projeto{i}')
                qty = request.POST.get(f'qty_projeto{i}')
                value = request.POST.get(f'value_projeto{i}')
                equipamento = Equipamento(pn=pn, descricao=descr)
                try:
                    equipamento.save()
                except:
                    messages.error(request, 'Erro ao cadastrar Produto!! Contate o administrador do site!')
                equip_proj = Equip_Projeto(name=pn, id_projeto=self.registro_proj, id_equip=equipamento, valor=value,
                                           qty=qty, atualizado=True)
                try:
                    equip_proj.save()
                except:
                    messages.error(request, 'Erro ao cadastrar Produto!! Contate o administrador do site!')
            else:
                break

        for j in range(self.acessorio_number, 10000):
            if request.POST.get(f'ac_pn_projeto{j}'):
                pn = request.POST.get(f'ac_pn_projeto{j}')
                descr = request.POST.get(f'ac_desc_projeto{j}')
                qty = request.POST.get(f'ac_qty_projeto{j}')
                value = request.POST.get(f'ac_value_projeto{j}')
                equipamento = Equipamento(pn=pn, descricao=descr, is_acessorio=True)
                try:
                    equipamento.save()
                except:
                    messages.error(request, 'Erro ao cadastrar Acessório!! Contate o administrador do site!')
                equip_proj = Equip_Projeto(id_projeto=self.registro_proj, id_equip=equipamento, valor=value, qty=qty,
                                           atualizado=True)
                try:
                    equip_proj.save()
                except:
                    messages.error(request, 'Erro ao cadastrar Acessório!! Contate o administrador do site!')
            else:
                break
        self.registro_proj_r.registro_atualizacao = True
        self.registro_proj_r.data_att_registro = timezone.now()
        self.registro_proj_r.save()
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.registro,
            'registros': self.registro,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }
        return render(request, self.template_name, self.contexto)


class DetalheIndex(View):
    template_name = 'Detalhes/detalhe.html'

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
            self.id_user = request.user

            pk = self.kwargs.get('pk')
            self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa

            if not self.vendedor_user:
                if self.revenda_user_id.is_admin:
                    self.registro = Registro.objects.get(id_revenda=self.revenda_user_id.revenda, pk=pk, marca=self.empresa)
                else:
                    self.registro = Registro.objects.get(id_revenda_user=self.revenda_user_id, pk=pk, marca=self.empresa)
            else:
                self.registro = Registro.objects.get(pk=pk, marca=self.empresa)
            self.id_projeto = self.registro.id_projeto
            self.pns = Equip_Projeto.objects.filter(id_projeto=self.id_projeto)
            self.i = self.j = None
            for self.pn in self.pns:
                if self.pn.id_equip.is_acessorio:
                    self.j = 1
                else:
                    self.i = 1

            self.time = timezone.now()
            if self.registro.date_validade:
                self.time = self.registro.date_validade >= self.time.date()
            else:
                self.time = True
            if request.user.is_authenticated:
                nome = request.user.first_name.strip().split(' ')[0]
            else:
                nome = None
            today = timezone.now().date()
            self.contexto = {
                'today': today,
                'nome': nome,
                'aprovado': True,
                'time': self.time,
                'empresa': self.empresa,
                'is_gerente': self.vendedor_user,
                'i': self.i,
                'j': self.j,
                'registro': self.registro,
                'pnss': self.pns,
                'users': request.user.is_authenticated,
            }
        else:
            return redirect('/')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, self.template_name, self.contexto)
        else:
            messages.error(request, 'Logue no sistema para continuar!')
            return redirect('/')

class DetalheRevendaIndex(View):
    template_name = 'Detalhes/aprovar_revenda_detalhe.html'

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
        pk = self.kwargs.get('pk')
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        try:
            self.revenda_user = Revenda_User.objects.get(pk=pk)
        except:
            self.revenda_user = None
        if self.revenda_user.aprovado:
            return redirect('index')
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'registro': self.revenda_user,
            'empresa': self.empresa,
            'is_gerente': self.vendedor_user,
            'revenda': self.revenda_user,
            'users': request.user.is_authenticated,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class DetalheAprovarRevenda(View):
    model = 'Revenda_User'
    template_name = 'Detalhes/aprovar_revenda_detalhes.html'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        self.id_user = request.user
        try:
            self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        except:
            self.vendedor_user = None
        self.registros_att = Registro.objects.filter(atualizado=False)
        self.count_registro = len(self.registros_att)
        self.revenda_u = Revenda_User.objects.filter(aprovado=False)
        page = request.GET.get('page', 1)
        paginator = Paginator(self.revenda_u, 6)
        try:
            self.revenda_u = paginator.page(page)
        except PageNotAnInteger:
            self.revenda_u = paginator.page(1)
        except EmptyPage:
            self.revenda_u = paginator.page(paginator.num_pages)

        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'revendas': self.revenda_u,
            'empresa': self.empresa,
            'number_registro': self.count_registro,
            'vendedor_gerente': self.vendedor_user,
            'vendedor': self.vendedor_user,
            'user': self.revenda_u,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class PostBusca(View):
    template_name = 'Detalhes/busca.html'
    model = 'Registro'
    vendedores = Vendedor.objects.all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        termo = self.request.GET.get('termo')
        self.id_user = request.user
        try:
            self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        except:
            self.vendedor_user = None
        self.registros_att = Registro.objects.filter(atualizado=False, marca=self.empresa)
        self.count_registro = len(self.registros_att)
        if self.vendedor_user:
            qs = Registro.objects.filter(
                Q(id_revenda__cnpj__icontains=termo) | Q(id_cliente__cnpj__icontains=termo) | Q(rede__icontains=termo) | Q(id_cliente__email__icontains=termo)
            ).filter(marca=self.empresa).order_by('-date_entered')
        else:
            self.revenda_user_id = Revenda_User.objects.get(user_revenda=self.id_user)
            if self.revenda_user_id.is_admin:
                self.revenda = Revenda.objects.filter(revenda_user__user_revenda=self.id_user).first()
                self.registro = Registro.objects.filter(id_revenda=self.revenda, marca=self.empresa).order_by(
                    '-date_entered')
                qs = Registro.objects.filter(
                    Q(id_revenda__cnpj__icontains=termo) | Q(id_cliente__cnpj__icontains=termo) | Q(rede__icontains=termo) | Q(id_cliente__email__icontains=termo)
                ).filter(id_revenda=self.revenda, marca=self.empresa).order_by('-date_entered')
            else:
                self.registro = Registro.objects.filter(id_revenda_user=self.revenda_user_id, marca=self.empresa)
                qs = Registro.objects.filter(
                    Q(id_revenda__cnpj__icontains=termo) | Q(id_cliente__cnpj__icontains=termo) | Q(rede__icontains=termo) | Q(id_cliente__email__icontains=termo)
                ).filter(id_revenda_user=self.revenda_user_id,  marca=self.empresa).order_by('-date_entered')
        page = request.GET.get('page', 1)
        paginator = Paginator(qs, 6)
        try:
            self.registro = paginator.page(page)
        except PageNotAnInteger:
            self.registro = paginator.page(1)
        except EmptyPage:
            self.registro = paginator.page(paginator.num_pages)
        self.empresa = Url.objects.get(url=request.META['HTTP_HOST']).empresa
        if request.user.is_authenticated:
            nome = request.user.first_name.strip().split(' ')[0]
        else:
            nome = None
        today = timezone.now().date()
        self.contexto = {
            'today': today,
            'nome': nome,
            'aprovado': True,
            'empresa': self.empresa,
            'vendedor_gerente': self.vendedor_user,
            'number_registro': self.count_registro,
            'vendedor': self.vendedor_user,
            'termo': termo,
            'registros': self.registro,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
            'filters': qs,
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)


class Aprovar(DetalhesIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST.get('numero_registro'):
            messages.error(request, 'Numero do Registro não inserido!!')
            return render(request, self.template_name, self.contexto)
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        if self.vendedor_user:
            self.pk = self.kwargs.get('pk')
            self.numero = request.POST.get("numero_registro")
            self.registro_update = Registro.objects.get(pk=self.pk)
            self.registro_update.atualizado = True
            self.registro_update.status = True
            self.registro_update.registro_atualizacao = False
            self.registro_update.date_atualizado = timezone.now()
            self.registro_update.date_validade = timezone.now() + timedelta(days=30)
            self.registro_update.numero_registro = self.numero
            try:
                self.registro_update.save()
                messages.success(request, 'Aprovado com sucesso!!')
            except:
                messages.error(request, 'Falha ao Aprovar.')
            self.projeto = self.registro_update.id_projeto.id
            self.projeto_update_q = Projeto.objects.get(pk=self.projeto)
            for j in range(10000):
                if request.POST.get(f'pn_projeto{j}'):
                    pn = request.POST.get(f'pn_projeto{j}')
                    self.projeto_update = Equip_Projeto.objects.get(id_projeto=self.projeto_update_q, name=pn)
                    if int(request.POST.get(f'aprovado_equip{j}')) == 1:
                        self.projeto_update.aprovado = True
                    else:
                        self.projeto_update.aprovado = False
                    self.projeto_update.atualizado = False
                    self.projeto_update.save()
                else:
                    break
            for k in range(10000):
                if request.POST.get(f'ac_pn_projeto{k}'):
                    pn = request.POST.get(f'ac_pn_projeto{k}')
                    self.projeto_update = Equip_Projeto.objects.get(id_projeto=self.projeto_update_q, name=pn)
                    if int(request.POST.get(f'aprovado_acess{k}')) == 1:
                        self.projeto_update.aprovado = True
                    else:
                        self.projeto_update.aprovado = False
                    self.projeto_update.atualizado = False
                    self.projeto_update.save()
                else:
                    break
            self.url_bd = request.META['HTTP_HOST']
            self.enviaEmail()
            conexao = pymysql.connect(host='52.86.229.161',db='crmaidchomologa', user='MysqlArtico', passwd='db2019AIDC#Crm')
            cursor = conexao.cursor()
            cursor.execute("SELECT token_portal_c FROM users_cstm where id_c = '9ca8e62a-4cb0-8307-5cc4-5c9a77835baf'")
            resultado = cursor.fetchall()
            for result in resultado:
                self.token = result[0]

            name = f"{self.registro_update.id_cliente}/Portal Oportunidade"
            jsonstr = {
                "token": f"{self.token}",
                "empresa": f"{self.empresa}",
                "fase": "1",
                "emailRV": f"aaaa.com",
                "nameRV": f"{self.registro_update.id_revenda.razao_social}",
                "CNPJRV": f"{self.registro_update.id_revenda.cnpj}",
                "TelefoneRV": f"{self.registro_update.id_revenda.telefone}",
                "CidadeRV": f"{self.registro_update.id_revenda.cidade}",
                "EstadoRV": f"{self.registro_update.id_revenda.estado}",
                "CEPRV": f"{self.registro_update.id_revenda.cep}",
                "RuaRV": f"{self.registro_update.id_revenda.rua}",
                "nameClient": f"{self.registro_update.id_cliente.razao_social}",
                "email": f"aa@aa.com",
                "CNPJ": f"{self.registro_update.id_cliente.cnpj}",
                "Telefone": f"{self.registro_update.id_cliente.telefone}",
                "Cidade": f"{self.registro_update.id_cliente.cidade}",
                "CEP": f"{self.registro_update.id_cliente.cep}",
                "Rua": f"{self.registro_update.id_cliente.rua}",
                "Estado": f"{self.registro_update.id_cliente.estado}",
                "contato": f"{self.registro_update.contato}",
                "registro_id": f"{self.pk}",
                "registro_numero": f"{self.numero}",
                "data_validade": f"{self.registro_update.date_validade}",
                "name": f"{name}",
            }
            requests.post("http://crmalpha.grupo-artico.com/index.php?entryPoint=OportunidadeCotacaoPortal",
                          json=jsonstr)
            proj = Equip_Projeto.objects.filter(id_projeto=self.projeto_update_q)
            for i in proj:
                jsonstr2 = {
                    "token": f"{self.token}",
                    "fase": "2",
                    "registro_id": f"{self.pk}",
                    "namePN": f"{i.name}",
                    "valorPN": f"{i.valor}",
                    "qtyPN": f"{i.qty}",
                    "descrPN": f"{i.id_equip.descricao}"
                }
                requests.post(
                    "http://crmalpha.grupo-artico.com/index.php?entryPoint=OportunidadeCotacaoPortal",
                    json=jsonstr2)
            return render(request, self.template_name, self.contexto)
        else:
            return render(request, self.template_name, self.contexto)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def enviaEmail(self):
        print("HERE")
        emails = Gerente.objects.get(url__url=self.url_bd, nome='noreply')
        me = emails.email
        you = self.registro_update.id_revenda_user.user_revenda.email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Registro de Oportunidade Aprovado"
        msg['From'] = me
        self.url = f'http://{self.url_bd}/pt/Detalhe/Detalhe/{self.pk}'

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
        									  <h1 style='margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;'>Registro de Oportunidade para o cliente {self.registro_update.id_cliente} foi aprovado com sucesso! Validade: 30 dias.</h1>
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
        												  <a href='{self.url}' target='_blank' style='display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;'>Link Para o Registro</a>
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
        									  <p style='margin: 0;'>Clique no link acima para ter acesso ao Registro.</p>
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

        email_aux = "gabriel.santos@primeinterway.com.br"
        emails = Gerente.objects.filter(url__url=self.url_bd)
        for email in emails:
            print(email)
            email_aux = str(email) + ", " + email_aux
        msg["To"] = you+", " + email_aux
        s.sendmail(me, msg["To"].split(","), msg.as_string())
        s.quit()
        return

class Aprovar_Revenda(DetalhesIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        if self.vendedor_user:
            self.pk = self.kwargs.get('pk')
            self.revenda_user = Revenda_User.objects.get(pk=self.pk)
            self.revenda_i = Revenda_User.objects.get(pk=self.pk).revenda
            self.revenda_user.aprovado = True
            self.revenda_user.is_admin = True
            try:
                self.revenda_user.save()
            except:
                messages.error(request, 'Erro ao aprovar, contate o admnistrador do sistema!!')
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
        you = self.revenda_user.user_revenda.email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Cadastro de Revenda Aprovado"
        msg['From'] = me
        self.url = f'http://{self.url_bd}/pt'
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
        									  <h1 style='margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;'>Cadastro da Revenda {self.revenda_i} foi aprovado!</h1>
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
        												  <a href='{self.url}' target='_blank' style='display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;'>Link Para o Portal</a>
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
        									  <p style='margin: 0;'>Clique no link acima para ter acesso ao Portal.</p>
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
        email_aux = "gabriel.santos@primeinterway.com.br"
        emails = Gerente.objects.filter(url__url=self.url_bd)
        for email in emails:
            print(email)
            email_aux = str(email)+", "+email_aux
        msg["To"] = you+", "+email_aux
        s.sendmail(me, msg["To"].split(","), msg.as_string())
        s.quit()
        return


class Reprovar(DetalhesIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        if self.vendedor_user:
            self.pk = self.kwargs.get('pk')
            self.numero = request.POST.get("numero_registro")
            self.registro_update = Registro.objects.get(pk=self.pk)
            self.registro_update.atualizado = True
            self.registro_update.status = False
            self.registro_update.date_atualizado = timezone.now()

            self.url_bd = request.META['HTTP_HOST']
            self.enviaEmail()
            self.registro_update.save()
            messages.success(request, 'Reprovado com sucesso!!')
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
        msg['Subject'] = "Registro de Oportunidade Negado"
        msg['From'] = me
        self.url = f'http://{self.url_bd}/pt/Detalhe/Detalhe/{self.pk}'

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
									  <h1 style='margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;'>Registro de Oportunidade para o cliente {self.registro_update.id_cliente} foi negado!</h1>
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
												  <a href='{self.url}' target='_blank' style='display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;'>Link Para o Registro</a>
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
									  <p style='margin: 0;'>Clique no link acima para ter acesso ao Registro.</p>
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
        email_aux = "gabriel.santos@primeinterway.com.br"
        emails = Gerente.objects.filter(url__url=self.url_bd)
        for email in emails:
            print(email)
            email_aux = str(email) + ", " + email_aux
        msg["To"] = you + ", " + email_aux
        s.sendmail(me, msg["To"].split(","), msg.as_string())
        s.quit()
        return




class Reprovar_Revenda(DetalhesIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        if self.vendedor_user:
            pk = self.kwargs.get('pk')
            self.revenda_user = Revenda_User.objects.get(pk=pk)
            self.revenda_i = Revenda_User.objects.get(pk=pk).revenda
            self.revenda = self.revenda_user.revenda
            self.user_rv = self.revenda_user.user_revenda
            self.url_bd = request.META['HTTP_HOST']
            self.enviaEmail()
            self.revenda_user.delete()
            self.revenda.delete()
            self.user_rv.delete()

            return render(request, self.template_name, self.contexto)
        else:
            return render(request, self.template_name, self.contexto)

    def get_queryset(self):
        self.vendedor_user = Vendedor.objects.get(user_vendedor=self.id_user).is_gerente
        qs = super().get_queryset()
        return qs

    def enviaEmail(self):
        me = "gabriel.santos@primeinterway.com.br"
        you = self.revenda_user.user_revenda.email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Cadastro de Revenda não aprovado"
        msg['From'] = me
        self.url = f'http://{self.url_bd}/pt/'
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
                    									  <h1 style='margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;'>Cadastro da Revenda {self.revenda_i} não foi aprovado!</h1>
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
                    												  <a href='{self.url}' target='_blank' style='display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;'>Link Para o Portal</a>
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
                    									  <p style='margin: 0;'>Clique no link acima para ter acesso ao Portal.</p>
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
        email_aux = "gabriel.santos@primeinterway.com.br"
        emails = Gerente.objects.filter(url__url=self.url_bd)
        for email in emails:
            print(email)
            email_aux = str(email) + ", " + email_aux
        msg["To"] = you + ", " + email_aux
        s.sendmail(me, msg["To"].split(","), msg.as_string())
        s.quit()
        return
