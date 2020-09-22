from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages, auth
import pymysql
from django.utils import timezone
from .models import Projeto, Registro, Url
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
class MyApphook(CMSApp):
    app_name = "myapp"  # must match the application namespac
    name = "My Apphook"


    def get_urls(self, page=None, language=None, **kwargs):
        return ["Registro.urls"]

    def init_toolbar(self, request):
        self.request = request
        self.is_staff = self.request.user.is_staff
        self.edit_mode = self.is_staff and self.request.session.get('cms_edit', False)
        self.show_toolbar = self.is_staff or self.request.session.get('cms_edit', False)
        self.show_toolbar = False
        if self.request.session.get('cms_toolbar_disabled', True):
            self.show_toolbar = False


class RegistroIndex(View):
    model = 'Registro'
    template_name = 'sidebar_left.html'
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
        self.contexto = {
            'index': True,
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
        self.contexto = {
            'index': True,
            'aprovado': self.revenda_user_aprovado,
            'today': today,
            'nome': nome,
            'empresa': self.empresa,
            'revendas': self.revendas,
            'users': request.user.is_authenticated,
            'vendedores': self.vendedores,
            'cnpj_cliente': request.POST.get("cnpj_cliente"),
            'contact_cliente': request.POST.get("contact_cliente"),
            'razao_cliente': request.POST.get("razao_cliente"),
            'cep_cliente': request.POST.get("cep_cliente"),
            'address_cliente': request.POST.get("address_cliente"),
            'city_cliente': request.POST.get("city_cliente"),
            'state_cliente': request.POST.get("state_cliente"),
            'email_cliente': request.POST.get("email_cliente"),
            'phone_cliente': request.POST.get("phone_cliente"),
            'aplication_projeto': request.POST.get("aplication_projeto"),
            'esp_projeto': request.POST.get("esp_projeto"),
            'colet_projeto': request.POST.get("colet_projeto"),
            'info_projeto': request.POST.get("info_projeto"),
            'concl_projeto': request.POST.get("concl_projeto"),
            'vendedor': request.POST.get("vendedor"),
        }
        if request.POST.get('cnpj_revenda'):
            if request.method != 'POST':
                return render(request, 'Registro/index.html')
            try:
                self.cnpj_rev = Revenda.objects.get(cnpj=request.POST.get('cnpj_revenda'))
                messages.error(request, 'Erro!! Revenda já Cadastrada no Sistema!')
                return render(request, 'Registro/index.html')
            except:
                try:
                    self.cnpj_rev = Revenda.objects.get(cnpj=request.POST.get('cnpj_revenda'))
                except:
                    self.cnpj_rev = None
                if not self.cnpj_rev:
                    cnpj = request.POST.get('cnpj_revenda')
                    razao = request.POST.get('razao_revenda')
                    address = request.POST.get('address_revenda')
                    state = request.POST.get('state_revenda')
                    cep = request.POST.get('cep_revenda')
                    cidade = request.POST.get('city_revenda')
                    telefone = request.POST.get('telefone_revenda')
                    contato = request.POST.get('contato_revenda')

                    revenda = Revenda(razao_social=razao, cnpj=cnpj, rua=address, cidade=cidade, estado=state, contato=contato, cep=cep, telefone=telefone)
                    nome = request.POST.get('name')
                    email = request.POST.get('email')
                    senha = request.POST.get('pwd')
                    senha2 = request.POST.get('pwd2')
                    revenda_user_o = revenda

                    if not nome or not email or not senha or not senha2:
                        messages.error(request, 'Campo Vazio!')
                        return render(request, 'Registro/index.html')
                    try:
                        validate_email(email)
                    except:
                        messages.error(request, 'Email Invalido')
                        return render(request, self.template_name, self.contexto)
                    try:
                        email_ex = User.objects.get(email=email)
                    except:
                        email_ex = None
                    if email_ex:
                        messages.error(request, 'E-mail já cadastrado')
                        return render(request, self.template_name, self.contexto)
                    if len(senha) <= 6:
                        messages.error(request, 'Senha curta')
                        return render(request, self.template_name, self.contexto)
                    if senha != senha2:
                        messages.error(request, 'Senhas não conferem!')
                        return render(request, self.template_name, self.contexto)
                    if User.objects.filter(email=email).exists():
                        messages.error(request, 'Email já existe')
                        return render(request, self.template_name, self.contexto)
                    user = User.objects.create_user(username=email, email=email, password=senha, first_name=nome)
                    try:
                        user.save()
                    except:
                        messages.error(request, 'Falha ao se cadastrar! Contacte o administrador do site!')
                        return render(request, self.template_name, self.contexto)
                    try:
                        revenda.save()
                        user_revenda = Revenda_User(nome=nome, revenda=revenda_user_o, user_revenda=user, aprovado=False)
                        user_revenda.save()
                        messages.success(request, 'Revenda cadastrada com sucesso!')
                        return render(request, self.template_name, self.contexto)
                    except:
                        messages.error(request, 'Falha ao se cadastrar! Contacte o administrador do site!')
                        return render(request, self.template_name, self.contexto)

        elif request.POST.get('email_cadastro'):
            if request.method != 'POST':
                return render(request, 'Registro/index.html')
            nome = request.POST.get('name_cadastro')
            email = request.POST.get('email_cadastro')
            senha = request.POST.get('pwd_cadastro')
            senha2 = request.POST.get('pwd_cadastro2')
            user = request.user
            revenda_user_o = Revenda_User.objects.get(user_revenda=user).revenda

            if not nome or not email or not senha or not senha2:
                messages.error(request, 'Campo Vazio!')
                return render(request, 'Registro/index.html')
            try:
                validate_email(email)
            except:
                messages.error(request, 'Email Invalido')
                return render(request,self.template_name, self.contexto)
            try:
                email_ex = User.objects.get(email=email)
            except:
                email_ex = None
            if email_ex:
                messages.error(request, 'E-mail já cadastrado')
                return render(request, self.template_name, self.contexto)
            if len(senha) < 6:
                messages.error(request, 'Senha curta')
                return render(request, self.template_name, self.contexto)
            if senha != senha2:
                messages.error(request, 'Senhas não conferem!')
                return render(request, self.template_name, self.contexto)
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email já existe')
                return render(request, self.template_name, self.contexto)
            user = User.objects.create_user(username=email, email=email, password=senha, first_name=nome)
            try:
                user.save()
            except:
                messages.error(request, 'Falha ao se cadastrar! Contacte o administrador do site!')
                return render(request, self.template_name, self.contexto)
            try:
                user_revenda = Revenda_User(nome=nome, revenda=revenda_user_o, user_revenda=user, aprovado=True)
                user_revenda.save()
                messages.success(request, 'Cadastrado com sucesso!')
                return redirect('index')
            except:
                messages.error(request, 'Falha ao se cadastrar! Contacte o administrador do site!')
                return render(request, self.template_name, self.contexto)
        if request.POST.get("cnpj_cliente") == '':
            messages.error(request, 'Inserir o CNPJ do cliente')
            return render(request, self.template_name, self.contexto)
        try:
            id_cliente_b = Cliente_Final.objects.get(cnpj=request.POST.get("cnpj_cliente"))
            rede = request.POST.get("rede_cliente")
        except:
            cnpj_cliente = request.POST.get("cnpj_cliente")
            razao_cliente = request.POST.get("razao_cliente")
            address_cliente = request.POST.get("address_cliente")
            city_cliente = request.POST.get("city_cliente")
            state_cliente = request.POST.get("state_cliente")
            email_cliente = request.POST.get("email_cliente")
            phone_cliente = request.POST.get("phone_cliente")
            cep_cliente = request.POST.get("cep_cliente")
            rede = request.POST.get("rede_cliente")
            if razao_cliente == '' or address_cliente == '' or city_cliente == '' or state_cliente == '' or email_cliente == '' or phone_cliente == '':
                messages.error(request, 'Inserir informações do cliente')
                return render(request, self.template_name, self.contexto)
            cliente = Cliente_Final(cep=cep_cliente ,razao_social=razao_cliente, cnpj=cnpj_cliente, rua=address_cliente, cidade=city_cliente, estado=state_cliente, telefone=phone_cliente, email=email_cliente, rede=rede)
            try:
                cliente.save()
                id_cliente_b = cliente
            except:
                messages.error(request, 'Erro ao cadastrar Cliente!! Contate o administrador do site!')
                return render(request, self.template_name, self.contexto)

        self.id_user = request.user
        self.revenda_user_id = Revenda_User.objects.get(user_revenda=self.id_user)
        self.revenda_id = Revenda.objects.get(pk=self.revenda_user_id.revenda.id)
        revenda_id_b = self.revenda_id
        try:
            aplication_projeto = request.POST.get("aplication_projeto")
            esp_projeto = request.POST.get("esp_projeto")
            homologa_projeto = request.POST.get("homologa_projeto")
            if homologa_projeto == 'sim':
                homologa_projeto=True
            else:
                homologa_projeto=False

            colet_projeto = request.POST.get("colet_projeto")
            parc_projeto = request.POST.get("parc_projeto")
            concl_projeto = request.POST.get("concl_projeto")
            info_projeto = request.POST.get("info_projeto")
            if aplication_projeto == '' or esp_projeto == '' or colet_projeto == '' or parc_projeto == '' or concl_projeto == '':
                messages.error(request, 'Inserir informações do Projeto')
                return render(request, self.template_name, self.contexto)
            projeto = Projeto(aplicacao=aplication_projeto, esp_tec=esp_projeto, homologa=homologa_projeto, colet_dados=colet_projeto, parc_soft=parc_projeto, info_ad=info_projeto, date_concl=concl_projeto)
            projeto.save()
            projeto_id = projeto

            for i in range(10000):
                if request.POST.get(f'pn_projeto{i}'):
                    pn = request.POST.get(f'pn_projeto{i}')
                    descr = request.POST.get(f'desc_projeto{i}')
                    qty = request.POST.get(f'qty_projeto{i}')
                    value = str(request.POST.get(f'value_projeto{i}'))
                    value = value.replace("R$","")
                    value = value.replace("$","")
                    value = value.replace(" ","")
                    value = value.replace(",",".")
                    equipamento = Equipamento(pn=pn, descricao=descr)
                    equipamento.save()
                    equip_proj = Equip_Projeto(name=pn,id_projeto=projeto_id, id_equip=equipamento, valor=value, qty=qty, number=i)
                    equip_proj.save()
                else:
                    break

            for j in range(10000):
                if request.POST.get(f'ac_pn_projeto{j}'):
                    pn = request.POST.get(f'ac_pn_projeto{j}')
                    descr = request.POST.get(f'ac_desc_projeto{j}')
                    qty = request.POST.get(f'ac_qty_projeto{j}')
                    value = str(request.POST.get(f'ac_value_projeto{j}'))
                    value = value.replace("R$", "")
                    value = value.replace("$", "")
                    value = value.replace(" ", "")
                    value = value.replace(",", ".")
                    equipamento = Equipamento(pn=pn, descricao=descr, is_acessorio=True)
                    equipamento.save()
                    equip_proj = Equip_Projeto(id_projeto=projeto_id, id_equip=equipamento, valor=value, qty=qty, number=j, name=pn)
                    equip_proj.save()
                else:
                    break

            for j in range(10000):
                if request.POST.get(f'c_pn_projeto{j}'):
                    pn = request.POST.get(f'c_pn_projeto{j}')
                    descr = request.POST.get(f'c_desc_projeto{j}')
                    qty = request.POST.get(f'c_qty_projeto{j}')
                    value = str(request.POST.get(f'c_value_projeto{j}'))
                    value = value.replace("R$", "")
                    value = value.replace("$", "")
                    value = value.replace(" ", "")
                    value = value.replace(",", ".")
                    equipamento = Equipamento(pn=pn, descricao=descr, is_concorrente=True)
                    equipamento.save()
                    equip_proj = Equip_Projeto(id_projeto=projeto_id, id_equip=equipamento, valor=value, qty=qty, number=j, name=pn)
                    equip_proj.save()
                else:
                    break

            contact_cliente = request.POST.get("contact_cliente")
            vendedor = request.POST.get("vendedor")
            registro = Registro(marca=self.empresa, id_revenda=revenda_id_b, id_revenda_user=self.revenda_user_id, id_cliente=id_cliente_b, id_projeto=projeto_id, vendedor=vendedor, contato=contact_cliente, rede=rede)
            registro.save()
        except:
            messages.error(request, 'Erro ao cadastrar Registro!! Contate o administrador do site!')
            return render(request, self.template_name, self.contexto)

        return redirect('/?toolbar_off')


class RegistroEditIndex(RegistroIndex):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect('')


def login(request):
    if request.method != 'POST':
        return render(request, 'accounts/login.html')

    usuario = request.POST.get('email')
    senha = request.POST.get('pwd')

    user = auth.authenticate(request, username=usuario, password=senha)

    if not user:
        messages.error(request, 'Usuário ou senha inválidos.')
        return redirect('index')
    else:
        auth.login(request, user)
        messages.success(request, 'Você fez login com sucesso.')
        return redirect('index')


def logout(request):
    auth.logout(request)
    return redirect('index')
