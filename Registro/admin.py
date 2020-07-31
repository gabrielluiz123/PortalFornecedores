from django.contrib import admin
from .models import Registro, Projeto, Url, Gerente
from aldryn_apphooks_config.admin import ModelAppHookConfig, BaseAppHookConfig


class RegistroAdmin(ModelAppHookConfig, admin.ModelAdmin):
    list_display = ('id', 'id_revenda_user', 'id_revenda', 'id_cliente', 'status', 'vendedor', 'date_entered')
    list_display_links = ('id',)


class UrlAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa', 'url')
    list_display_links = ('id', 'empresa')


class ProjetoAdmin(ModelAppHookConfig, admin.ModelAdmin):
    list_display = ('id', 'homologa', 'parc_soft')
    list_display_links = ('id',)
    search_fields = ('aplicacao', 'esp_tec', 'colet_dados', 'info_ad')


class GerenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'url', 'email')
    list_display_links = ('id',)
    search_fields = ('nome', 'email', 'url')


admin.site.register(Url, UrlAdmin)
admin.site.register(Gerente, GerenteAdmin)
admin.site.register(Registro, RegistroAdmin)
admin.site.register(Projeto, ProjetoAdmin)
